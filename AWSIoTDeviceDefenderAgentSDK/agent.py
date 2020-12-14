# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   A copy of the License is located at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   or in the "license" file accompanying this file. This file is distributed
#   on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#   express or implied. See the License for the specific language governing
#   permissions and limitations under the License.


from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from AWSIoTDeviceDefenderAgentSDK import collector
import logging
import argparse
from time import sleep
from socket import gethostname
import cbor
import sys

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))

class IoTClientWrapper(object):
    """
    Wrapper around the AWS Iot Python SDK.

    Sets common parameters based on the AWS Iot Python SDK's `Basic PubSub`_ sample.

    .. _Basic PubSub: https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py

    """

    def __init__(self, endpoint, root_ca_path, certificate_path, private_key_path, client_id, signing_region, proxy_host, proxy_port, use_websocket):
        self.host = endpoint
        self.root_ca_path = root_ca_path
        self.certificate_path = certificate_path
        self.private_key_path = private_key_path
        self.client_id = client_id
        self.signing_region = signing_region
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.use_websocket = use_websocket
        self.iot_client = None

    def publish(self, publish_to_topic, payload):
        """Publish to MQTT"""
        publish_future, packet_id = self.iot_client.publish(
            topic=publish_to_topic,
            payload=payload,
            qos=mqtt.QoS.AT_MOST_ONCE)
        return publish_future

    def subscribe(self, subscribe_to_topic, callback):
        """Subscribe to MQTT"""
        subscribe_future, packet_id = self.iot_client.subscribe(
            topic=subscribe_to_topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=callback)

        subscribe_result = subscribe_future.result()
        print("Subscribed to "+subscribe_to_topic+" with "+str(subscribe_result['qos']))
        return subscribe_result

    def connect(self):
        """Connect to AWS IoT"""
        if not self.certificate_path or not self.private_key_path:
            print("Missing credentials for authentication.")
            exit(2)

        # Spin up resources
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        if self.use_websocket == True:
            proxy_options = None
            if (self.proxy_host):
                proxy_options = http.HttpProxyOptions(host_name=self.proxy_host, port=self.proxy_port)

            credentials_provider = auth.AwsCredentialsProvider.new_default_chain(client_bootstrap)
            self.iot_client = mqtt_connection_builder.websockets_with_default_aws_signing(
                endpoint=self.host,
                client_bootstrap=client_bootstrap,
                region=self.signing_region,
                credentials_provider=credentials_provider,
                websocket_proxy_options=proxy_options,
                ca_filepath=self.root_ca_path,
                on_connection_interrupted=on_connection_interrupted,
                on_connection_resumed=on_connection_resumed,
                client_id=self.client_id,
                clean_session=False,
                keep_alive_secs=6)

        else:
            self.iot_client = mqtt_connection_builder.mtls_from_path(
                endpoint=self.host,
                cert_filepath=self.certificate_path,
                pri_key_filepath=self.private_key_path,
                client_bootstrap=client_bootstrap,
                ca_filepath=self.root_ca_path,
                on_connection_interrupted=on_connection_interrupted,
                on_connection_resumed=on_connection_resumed,
                client_id=self.client_id,
                clean_session=False,
                keep_alive_secs=6)

        print("Connecting to {} with client ID '{}'...".format(
            self.host, self.client_id))

        connect_future = self.iot_client.connect()

        # Future.result() waits until a result is available
        connect_future.result()
        sleep(2)


def parse_args():
    """Setup Commandline Argument Parsing"""
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="endpoint",
                        help="Your AWS IoT custom endpoint, not including a port. " +
                        "Ex: \"abcd123456wxyz-ats.iot.us-east-1.amazonaws.com\"")
    parser.add_argument("-r", "--rootCA", action="store", dest="root_ca_path", required=True,
                        help="File path to root certificate authority, in PEM format. " +
                        "Necessary if MQTT server uses a certificate that's not already in " +
                        "your trust store.")
    parser.add_argument("-c", "--cert", action="store", dest="certificate_path", required=True,
                        help="File path to your client certificate, in PEM format.")
    parser.add_argument("-k", "--key", action="store", dest="private_key_path", required=True,
                        help="File path to your private key, in PEM format.")
    parser.add_argument("-id", "--client_id", action="store", dest="client_id", required=True,
                        help="MQTT Client id, used as thing name for metrics, unless one is passed as a parameter")
    parser.add_argument("-w", '--use-websocket', action="store", dest="use_websocket", default=False,
                        help="To use a websocket instead of raw mqtt. If you " +
                        "specify this option you must specify a region for signing, you can also enable proxy mode.")
    parser.add_argument("-se", '--signing-region', action="store", dest="signing_region", default='us-east-1', help="If you specify --use-web-socket, this " +
                        "is the region that will be used for computing the Sigv4 signature")
    parser.add_argument("-t", "--thing_name", action="store", dest="thing_name", required=False,
                        help="Thing to publish metrics for. If omitted, client_id is assumed")
    parser.add_argument("-d", "--dryrun", action="store_true", dest="dry_run", default=False,
                        help="Collect and print metrics to console, do not publish them over mqtt")
    parser.add_argument("-i", "--interval", action="store", dest="upload_interval", default=300,
                        help="Interval in seconds between metric uploads")
    parser.add_argument("-s", "--short_tags", action="store_true", dest="short_tags", default=False,
                        help="Use long-format field names in metrics report")
    parser.add_argument("-f", "--format", action="store", dest="format", required=True, choices=["cbor", "json"],
                        default='json', help="Choose serialization format for metrics report")
    parser.add_argument('-ph','--proxy-host', action="store", dest="proxy_host", help="Hostname for proxy to connect to. Note: if you use this feature, " +
                        "you will likely need to set --root-ca to the ca for your proxy.")
    parser.add_argument('-pp','--proxy-port', action="store", dest="proxy_port", type=int, default=8080, help="Port for proxy to connect to.")
    parser.add_argument('--verbosity', action="store", dest="verbosity", choices=[x.name for x in io.LogLevel], default=io.LogLevel.NoLogs.name,
                        help='Logging level')
    parser.add_argument('-cm','--include-custom-metrics','--custom-metrics', action="store_true", dest="custom_metrics", default=False, help="Adds custom metrics to payload.")
    return parser.parse_args()

def custom_callback(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    raw_payload = payload.decode('utf-8')
    if 'json' in topic:
        print(raw_payload)
    else:
        print(cbor.loads(payload))

        print("from topic: ")
        print(topic)
        print("--------------\n\n")

def main():
    # Read in command-line parameters
    args = parse_args()
    io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')
    if not args.dry_run:
        client_id = ""
        thing_name = ""

        if not args.client_id:
            client_id = gethostname()
        else:
            client_id = args.client_id
        
        if not args.thing_name:
            thing_name = client_id
        else:
            thing_name = args.thing_name

        iot_client = IoTClientWrapper(args.endpoint, args.root_ca_path,
                                      args.certificate_path, args.private_key_path, client_id,
                                      args.signing_region, args.proxy_host, args.proxy_port,
                                      args.use_websocket)
        iot_client.connect()

        # client_id must match a registered thing name in your account
        topic = "$aws/things/" + thing_name + "/defender/metrics/" + args.format

        # Subscribe to the accepted/rejected topics to indicate status of published metrics reports
        iot_client.subscribe(topic + "/accepted", custom_callback)
        iot_client.subscribe(topic + "/rejected", custom_callback)

    sample_rate = args.upload_interval

    #  Collector samples metrics from the system, it can track the previous metric to generate deltas
    coll = collector.Collector(args.short_tags, args.custom_metrics)

    metric = None
    first_sample = True  # don't publish first sample, so we can accurately report delta metrics
    while True:
        metric = coll.collect_metrics()
        if args.dry_run:
            print(metric.to_json_string(pretty_print=True))
            if args.format == 'cbor':
                with open("cbor_metrics", "w+b") as outfile:
                    outfile.write(bytearray(metric.to_cbor()))
        else:
            if first_sample:
                first_sample = False
            elif args.format == "cbor":
                iot_client.publish(topic, bytearray(metric.to_cbor()))
            else:
                iot_client.publish(topic, metric.to_json_string())

        sleep(float(sample_rate))

if __name__ == '__main__':
    main()
