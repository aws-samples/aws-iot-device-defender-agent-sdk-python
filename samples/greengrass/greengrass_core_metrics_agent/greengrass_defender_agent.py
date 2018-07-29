# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import logging
from time import sleep
import greengrasssdk
import psutil as ps

from AWSIoTDeviceDefenderAgentSDK import collector

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# You will need to use Local Resource Access to map the hosts /proc to a directory accessible in the lambda
ps.PROCFS_PATH = "/host_proc"
client = greengrasssdk.client('iot-data')
THING_NAME = "GREENGRASS_CORE_NAME"  # Thing name is the same as Greengrass Core Name
SAMPLE_RATE_SECONDS = 300  # 5 minute metrics


def function_handler(event, context):
    print "Lambda got event: " + str(event) + " context:" + str(context)


def publish_metrics():
    # thing name must match a registered thing name in your account
    topic = "$aws/things/" + THING_NAME + "/defender/metrics/json"

    try:
        metrics_collector = collector.Collector(short_metrics_names=False)
        while True:

            metric = metrics_collector.collect_metrics()
            client.publish(
                topic=topic,
                payload=metric.to_json_string())

            sleep(float(SAMPLE_RATE_SECONDS))

    except Exception as e:
        print "Error: " + str(e)
    return


# Kickstart the long-running lambda publisher
publish_metrics()
