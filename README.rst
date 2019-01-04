##########################################
AWS IoT Device Defender Agent SDK (Python)
##########################################

Example implementation of an AWS IoT Device Defender metrics collection agent,
and other Device Defender Python samples.

The provided sample agent can be used as a basis to implement a custom metrics collection agent.


*************
Prerequisites
*************

Minimum System Requirements
===========================

The Following requirements are shared with the `AWS IoT Device SDK for Python <https://github.com/aws/aws-iot-device-sdk-python>`_

-  Python 2.7+ or Python 3.3+ for X.509 certificate-based mutual authentication via port 8883 and MQTT over WebSocket protocol with AWS Signature Version 4 authentication
-  Python 2.7.10+ or Python 3.5+ for X.509 certificate-based mutual authentication via port 443
-  OpenSSL version 1.0.1+ (TLS version 1.2) compiled with the Python executable for X.509 certificate-based mutual authentication

Connect your Device to AWS IoT
==============================

If you have never connected your device to AWS IoT before, please follow the
`Getting Started with AWS IoT <https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html>`_
Guide. Make sure you note the location of your certificates, you will
need to provide the location of these to the Device Defender Sample
Agent.

****************************************
Notes on the sample agent implementation
****************************************
**client id**: The sample agent requires that the client id provided matches a "thing name" in your AWS IoT account. This only for the sake of making the sample easy to get started with. Device Defender only requires that metrics be published for things that are registered in your account, and does not impose any additional requirements on client id beyond those of the AWS IoT Platform. To customize this behavior, you can modify the way the agent generates the MQTT topic for publishing metrics reports, to use a value other than client id as the thing name portion of the topic.

**metric selection**: The sample agent attempts to gather all supported Device Defender metrics. Depending on your platform requirements and use case, you may wish to customize your agent to a subset of the metrics.

**********
Quickstart
**********

Installation
============

#. Clone the repository

.. code:: bash

   git clone https://github.com/aws-samples/aws-iot-device-defender-agent-sdk-python.git

#. Install Using pip

Pip is the easiest way to install the sample agent, it will take care of
installing dependencies

.. code:: bash

    pip install /path/to/sample/package

Running the Sample Agent
========================

.. code:: bash

    python agent.py --endpoint your.custom.endpoint.amazonaws.com  --rootCA /path/to/rootca  --cert /path/to/device/cert --format json -i 300

Command line options
--------------------

To see a summary of all commandline options:

.. code:: bash

    python agent.py --help


Test Metrics Collection Locally
-------------------------------

.. code:: bash

    python collector.py -n 1 -s 1


******************************
AWS IoT Greengrass Integration
******************************

Overview
========

AWS IoT Device Defender can be used in conjunction with AWS Greengrass.
Integration follows the standard Greengrass lambda deployment model,
making it easy to add AWS IoT Device Defender security to your
Greengrass Core devices.

Prerequisites
=============

#. `Greengrass environment setup <https://docs.aws.amazon.com/greengrass/latest/developerguide/module1.html>`__
#. `Greengrass core configured and running <https://docs.aws.amazon.com/greengrass/latest/developerguide/module2.html>`__
#. Ensure you can successfully deploy and run a lambda on your core

Using Device Defender with Greengrass Core devices
==================================================

You can deploy a Device Defender to your Greengrass core in two ways:

#. Using the pre-built Greengrass Device Defender Connector (*recommended*)
#. Create a lambda package manually

Using Greengrass Connector
--------------------------
The Device Defender Greengrass Connector provides the most streamlined and automated means of deploy the Device Defender agent to your
Greengrass core, and is the recommended method of using Device Defender with Greengrass.

For detailed information about using Greengrass Connectors see `Getting Started with Greengrass Connectors <https://docs.aws.amazon.com/greengrass/latest/developerguide/connectors-console.html>`__
For information about configuring the Device Defender Connector see `Device Defender Connector Details <https://docs.aws.amazon.com/greengrass/latest/developerguide/device-defender-connector.html>`__

#. Create a local resource to allow your lambda to collect metrics from the Greengrass Core host

   * Follow the instructions `here <https://docs.aws.amazon.com/greengrass/latest/developerguide/access-local-resources.html>`__
   * Use the following parameters:

     * **Resource Name:** ``Core_Proc``
     * **Type:** ``Volume``
     * **Source Path:** ``/proc``
     * **Destination Path:** ``/host_proc`` (make sure the same value is configured for the PROCFS_PATH environment variable above)
     * **Group owner file access permission:** "Automatically add OS group permissions of the Linux group that owns the resource"
     * Associate the resource with your metrics lambda

#. From the detail page of your Greengrass Group, click "Connectors" in the left-hand menu

#. Click the "Add a Connector" button

#. In the "Select a connector" screen, select the "Device Defender" connector from the list, click "Next"

#. On the "Configure parameters" screen, select the resource you created in Step 1, in the "Resource for /proc" box

#. In the "Metrics reporting interval" box, enter 300, or larger if you wish to use a longer reporting interval

#. Click the "add" button

#. `Deploy your connector to your Greengrass Group <https://docs.aws.amazon.com/greengrass/latest/developerguide/configs-core.html>`__


Create Your Lambda Package Manually
-----------------------------------

For this portion will be following the general process outlined
`here <https://docs.aws.amazon.com/greengrass/latest/developerguide/create-lambda.html/>`__

**Note:** Due to platform-specific binary extensions in the psutil package, this process should be performed on the platform where you
plan to deploy your lambda. 

#. Clone the AWS IoT Device Defender Python Samples Repository

   .. code:: bash

       git clone https://github.com/aws-samples/aws-iot-device-defender-agent-sdk-python.git

#. Create, and activate a virtual environment (optional, recommended)

   .. code:: bash

       pip install virtualenv
       virtualenv metrics_lambda_environment
       source metrics_lambda_environment/bin/activate

#. Install the AWS IoT Device Defender sample agent in the virtual
   environment Install from PyPi

   .. code:: bash

       pip install AWSIoTDeviceDefenderAgentSDK

   Install from downloaded source

   .. code:: bash

       cd aws-iot-device-defender-agent-sdk-python
       #This must be run from the same directory as setup.py
       pip install .

#. Create an empty directory to assemble your lambda, we will refer to
   this as your "lambda directory"

   .. code:: bash

       mkdir metrics_lambda
       cd metrics_lambda

#. Complete steps 1-4 from this
   `guide <https://docs.aws.amazon.com/greengrass/latest/developerguide/create-lambda.html>`__
#. Unzip the Greengrass python sdk into your lambda directory

   .. code:: bash

       unzip ../aws_greengrass_core_sdk/sdk/python_sdk_1_1_0.zip
       cp -R ../aws_greengrass_core_sdk/examples/HelloWorld/greengrass_common .
       cp -R ../aws_greengrass_core_sdk/examples/HelloWorld/greengrasssdk .
       cp -R ../aws_greengrass_core_sdk/examples/HelloWorld/greengrass_ipc_python_sdk .

#. Copy the AWSIoTDeviceDefenderAgentSDK module to the root level of
   your lambda

   .. code:: bash

       cp -R ../aws-iot-device-defender-agent-sdk-python/AWSIoTDeviceDefenderAgentSDK .

#. Copy the Greengrass agent to the root level of your lambda directory

   .. code:: bash

       cp ../aws-iot-device-defender-agent-sdk-python/samples/greengrass/greengrass_core_metrics_agent/greengrass_defender_agent.py .

#. Copy the dependencies from your virtual environment or your system, into the the root level of your lambda

   .. code:: bash

       cp -R ../metrics_lambda_environment/lib/python2.7/site-packages/psutil .
       cp -R ../metrics_lambda_environment/lib/python2.7/site-packages/cbor .

#. Create your lambda zipfile *Note: you should perform this command in
   the root level of your lambda directory*

   .. code:: bash

       rm *.zip
       zip -r greengrass_defender_metrics_lambda.zip *

Configure and deploy your Greengrass Lambda
-------------------------------------------

#. `Upload your lambda zip file <https://docs.aws.amazon.com/greengrass/latest/developerguide/package.html>`__
#. Select the Python 2.7 runtime, and enter ``greengrass_defender_agent.function_handler`` in the Handler field
#. `Configure your lambda as a long-lived lambda <https://docs.aws.amazon.com/greengrass/latest/developerguide/long-lived.html>`__
#. Configure the following environment variables:

   * **SAMPLE_INTERVAL_SECONDS:** The metrics generation interval. The default is 300 seconds.
     *Note: 5 minutes (300 seconds) is the shortest reporting interval supported by AWS IoT Device Defender*
   * **PROCFS_PATH:** The destination path that you will configure for your **/proc** resource as shown below.

#. `Configure a subscription from your lambda to the AWS IoT Cloud <https://docs.aws.amazon.com/greengrass/latest/developerguide/config_subs.html>`__
   *Note: For AWS IoT Device Defender, a subscription from AWS IoT Cloud to your lambda is not required*
#. Create a local resource to allow your lambda to collect metrics from the Greengrass Core host

   * Follow the instructions `here <https://docs.aws.amazon.com/greengrass/latest/developerguide/access-local-resources.html>`__
   * Use the following parameters:

     * **Resource Name:** ``Core_Proc``
     * **Type:** ``Volume``
     * **Source Path:** ``/proc``
     * **Destination Path:** ``/host_proc`` (make sure the same value is configured for the PROCFS_PATH environment variable above)
     * **Group owner file access permission:** "Automatically add OS group permissions of the Linux group that owns the resource"
     * Associate the resource with your metrics lambda

#. `Deploy your connector to your Greengrass Group <https://docs.aws.amazon.com/greengrass/latest/developerguide/configs-core.html>`__

Troubleshooting
---------------

Reviewing AWS IoT Device Defender device metrics using AWS IoT Console
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Temporarily modify your publish topic in your Greengrass lambda to
   something such as metrics/test
#. Deploy the lambda
#. Add a subscription to the temporary topic in the "Test" section of
   the iot console, shortly you should the metrics your Greengrass Core
   is emitting

**********************
Metrics Report Details
**********************

Overall Structure
=================

+-------------+--------------+------------+----------+---------------+--------------------------------------------------+
| Long Name   | Short Name   | Required   | Type     | Constraints   | Notes                                            |
+=============+==============+============+==========+===============+==================================================+
| header      | hed          | Y          | Object   |               | Complete block required for well-formed report   |
+-------------+--------------+------------+----------+---------------+--------------------------------------------------+
| metrics     | met          | Y          | Object   |               | Complete block required for well-formed report   |
+-------------+--------------+------------+----------+---------------+--------------------------------------------------+

Header Block
------------

+--------+--------+-------+------+--------+---------------------------------------------+
| Long   | Short  | Requi | Type | Constr | Notes                                       |
| Name   | Name   | red   |      | aints  |                                             |
+========+========+=======+======+========+=============================================+
| report | rid    | Y     | Inte |        | Monotonically increasing value, epoch       |
| \_id   |        |       | ger  |        | timestamp recommended                       |
+--------+--------+-------+------+--------+---------------------------------------------+
| versio | v      | Y     | Stri | Major. | Minor increments with addition of field,    |
| n      |        |       | ng   | Minor  | major increments if metrics removed         |
+--------+--------+-------+------+--------+---------------------------------------------+

Metrics Block
-------------

TCP Connections
^^^^^^^^^^^^^^^

+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+
| Long Name                  | Short Name   | Parent Element             | Required   | Type     | Constraints   | Notes                            |
+============================+==============+============================+============+==========+===============+==================================+
| tcp\_connections           | tc           | metrics                    | N          | Object   |               |                                  |
+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+
| established\_connections   | ec           | tcp\_connections           | N          | List     |               | ESTABLISHED TCP State            |
+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+
| connections                | cs           | established\_connections   | N          | List     |               |                                  |
+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+
| remote\_addr               | rad          | connections                | Y          | Number   | ip:port       | ip can be ipv6 or ipv4           |
+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+
| local\_port                | lp           | connections                | N          | Number   | >0            |                                  |
+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+
| local\_interface           | li           | connections                | N          | String   |               | interface name                   |
+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+
| total                      | t            | established\_connections   | N          | Number   | >= 0          | Number established connections   |
+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+
|                            |              |                            |            |          |               |                                  |
+----------------------------+--------------+----------------------------+------------+----------+---------------+----------------------------------+

Listening TCP Ports
^^^^^^^^^^^^^^^^^^^

+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| Long Name               | Short Name   | Parent Element          | Required   | Type     | Constraints   | Notes                         |
+=========================+==============+=========================+============+==========+===============+===============================+
| listening\_tcp\_ports   | tp           | metrics                 | N          | Object   |               |                               |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| ports                   | pts          | listening\_tcp\_ports   | N          | List     | > 0           |                               |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| port                    | pt           | ports                   | N          | Number   | >= 0          | ports should be numbers > 0   |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| interface               | if           | ports                   | N          | String   |               | Interface Name                |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| total                   | t            | listening\_tcp\_ports   | N          | Number   | >= 0          |                               |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+

Listening UDP Ports
^^^^^^^^^^^^^^^^^^^

+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| Long Name               | Short Name   | Parent Element          | Required   | Type     | Constraints   | Notes                         |
+=========================+==============+=========================+============+==========+===============+===============================+
| listening\_udp\_ports   | up           | metrics                 | N          | Object   |               |                               |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| ports                   | pts          | listening\_udp\_ports   | N          | List     | > 0           |                               |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| port                    | pt           | ports                   | N          | Number   | > 0           | ports should be numbers > 0   |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| interface               | if           | ports                   | N          | String   |               | Interface Name                |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+
| total                   | t            | listening\_udp\_ports   | N          | Number   | >= 0          |                               |
+-------------------------+--------------+-------------------------+------------+----------+---------------+-------------------------------+

Network Stats
^^^^^^^^^^^^^

+------------------+--------------+------------------+------------+----------+----------------------+---------+
| Long Name        | Short Name   | Parent Element   | Required   | Type     | Constraints          | Notes   |
+==================+==============+==================+============+==========+======================+=========+
| network\_stats   | ns           | metrics          | N          | Object   |                      |         |
+------------------+--------------+------------------+------------+----------+----------------------+---------+
| bytes\_in        | bi           | network\_stats   | N          | Number   | Delta Metric, >= 0   |         |
+------------------+--------------+------------------+------------+----------+----------------------+---------+
| bytes\_out       | bo           | network\_stats   | N          | Number   | Delta Metric, >= 0   |         |
+------------------+--------------+------------------+------------+----------+----------------------+---------+
| packets\_in      | pi           | network\_stats   | N          | Number   | Delta Metric, >= 0   |         |
+------------------+--------------+------------------+------------+----------+----------------------+---------+
| packets\_out     | po           | network\_stats   | N          | Number   | Delta Metric, >= 0   |         |
+------------------+--------------+------------------+------------+----------+----------------------+---------+

Sample Metrics Reports
======================

Long Field Names
----------------

.. code:: javascript

    {
        "header": {
            "report_id": 1529963534,
            "version": "1.0"
        },
        "metrics": {
            "listening_tcp_ports": {
                "ports": [
                    {
                        "interface": "eth0",
                        "port": 24800
                    },
                    {
                        "interface": "eth0",
                        "port": 22
                    },
                    {
                        "interface": "eth0",
                        "port": 53
                    }
                ],
                "total": 3
            },
            "listening_udp_ports": {
                "ports": [
                    {
                        "interface": "eth0",
                        "port": 5353
                    },
                    {
                        "interface": "eth0",
                        "port": 67
                    }
                ],
                "total": 2
            },
            "network_stats": {
                "bytes_in": 1157864729406,
                "bytes_out": 1170821865,
                "packets_in": 693092175031,
                "packets_out": 738917180
            },
            "tcp_connections": {
                "established_connections":{
                    "connections": [
                        {
                        "local_interface": "eth0",
                        "local_port": 80,
                        "remote_addr": "192.168.0.1:8000"
                        },
                        {
                        "local_interface": "eth0",
                        "local_port": 80,
                        "remote_addr": "192.168.0.1:8000"
                        }
                    ],
                    "total": 2
                }
            }
        }
    }

Short Field Names
-----------------

.. code:: javascript

    {
        "hed": {
            "rid": 1529963534,
            "v": "1.0"
        },
        "met": {
            "tp": {
                "pts": [
                    {
                        "if": "eth0",
                        "pt": 24800
                    },
                    {
                        "if": "eth0",
                        "pt": 22
                    },
                    {
                        "if": "eth0",
                        "pt": 53
                    }
                ],
                "t": 3
            },
            "up": {
                "pts": [
                    {
                        "if": "eth0",
                        "pt": 5353
                    },
                    {
                        "if": "eth0",
                        "pt": 67
                    }
                ],
                "t": 2
            },
            "ns": {
                "bi": 1157864729406,
                "bo": 1170821865,
                "pi": 693092175031,
                "po": 738917180
            },
            "tc": {
                "ec":{
                    "cs": [
                        {
                        "li": "eth0",
                        "lp": 80,
                        "rad": "192.168.0.1:8000"
                        },
                        {
                        "li": "eth0",
                        "lp": 80,
                        "rad": "192.168.0.1:8000"
                        }
                    ],
                    "t": 2
                }
            }
        }
    }

*****************
API Documentation
*****************
Can you can find the API documentation `here <https://aws-iot-device-defender-agent-sdk.readthedocs.io/en/latest/>`__

**********
References
**********

-  `AWS Lambda: Creating a Deployment Package
   (Python) <https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html>`__
-  `Monitoring with AWS Greengrass
   Logs <https://docs.aws.amazon.com/greengrass/latest/developerguide/greengrass-logs-overview.html>`__
-  `Troubleshooting AWS Greengrass
   Applications <https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-troubleshooting.html>`__
-  `Access Local Resources with Lambda
   Functions <https://docs.aws.amazon.com/greengrass/latest/developerguide/access-local-resources.html>`__

*******
License
*******

This library is licensed under the Apache 2.0 License.

*******
Support
*******

If you have technical questions about the AWS IoT Device SDK, use the `AWS
IoT Forum <https://forums.aws.amazon.com/forum.jspa?forumID=210>`__.
For any other questions about AWS IoT, contact `AWS
Support <https://aws.amazon.com/contact-us>`__.
