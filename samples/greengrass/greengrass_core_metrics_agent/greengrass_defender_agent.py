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

import greengrasssdk
import logging
import os
import psutil as ps
from time import sleep

from AWSIoTDeviceDefenderAgentSDK import collector

MIN_INTERVAL_SECONDS = 300 # minimum sample interval at which metrics messages can be published

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

client = greengrasssdk.client('iot-data')

def function_handler(event, context):
    print "Lambda got event: " + str(event) + " context:" + str(context)

def publish_metrics():
    try:
        # You will need to use Local Resource Access to map the hosts /proc to a directory accessible in the lambda
        ps.PROCFS_PATH = os.environ['PROCFS_PATH']
        core_name = os.environ['AWS_IOT_THING_NAME']
        topic = "$aws/things/" + core_name + "/defender/metrics/json"

        sample_interval_seconds = os.environ['SAMPLE_INTERVAL_SECONDS']
        if sample_interval_seconds < MIN_INTERVAL_SECONDS:
            sample_interval_seconds = MIN_INTERVAL_SECONDS

        print "Collector running on device: " + core_name
        print "Metrics topic: " + topic
        print "Sampling interval: " + sample_interval_seconds + " seconds"

        metrics_collector = collector.Collector(short_metrics_names=False)
        while True:

            metric = metrics_collector.collect_metrics()
            client.publish(
                topic=topic,
                payload=metric.to_json_string())
            sleep(float(sample_interval_seconds))

    except Exception as e:
        print "Error: " + str(e)
    return


# Kickstart the long-running lambda publisher
publish_metrics()
