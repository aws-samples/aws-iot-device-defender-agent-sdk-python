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

from unittest.mock import patch
from unittest.mock import MagicMock
import psutil
from collections import namedtuple
import socket
from AWSIoTDeviceDefenderAgentSDK import collector, metrics

PATCH_MODULE_LOCATION_PS = "AWSIoTDeviceDefenderAgentSDK.collector.ps."
PATCH_MODULE_LOCATION_METRICS = "AWSIoTDeviceDefenderAgentSDK.collector.Metrics."

ipaddr_tuple = namedtuple('ipaddr_tuple', 'ip port')
net_connections_tuple = namedtuple('net_connections_tuple', 'fd family type laddr raddr status pid')
net_connections_fail_tuple = namedtuple('net_connections_tuple', 'fd family type laddr raddr pid')
if_addr_tuple = namedtuple('if_addr_tuple', 'family address netmask broadcast ptp')


class TestCollector(object):
    def __use_mock_net_if_addrs(self, return_value_input):
        self.net_if_addrs_patcher = patch(PATCH_MODULE_LOCATION_PS + "net_if_addrs", spec=psutil.net_if_addrs)
        self.mock_net_if_addrs_function = self.net_if_addrs_patcher.start()
        self.mock_net_if_addrs_result = return_value_input
        self.mock_net_if_addrs_function.return_value = self.mock_net_if_addrs_result

    def __use_mock_net_io_counters(self):
        self.net_io_counters_patcher = patch(PATCH_MODULE_LOCATION_PS + "net_io_counters", spec=psutil.net_io_counters)
        self.mock_net_io_counters_function = self.net_io_counters_patcher.start()
        self.mock_net_io_counters_result = MagicMock()
        self.mock_net_io_counters_function.return_value = self.mock_net_io_counters_result

    def __use_mock_net_connections(self, return_value_input):
        self.net_connections_patcher = patch(PATCH_MODULE_LOCATION_PS + "net_connections", spec=psutil.net_connections)
        self.mock_net_connections_function = self.net_connections_patcher.start()
        self.mock_net_connections_result = return_value_input
        self.mock_net_connections_function.return_value = self.mock_net_connections_result

    def __setup_net_connections(self):
        t1 = net_connections_tuple(fd=115, family=socket.AF_INET, type=socket.SOCK_STREAM,
                                   laddr=ipaddr_tuple(ip='10.0.0.1', port=11111),
                                   raddr=ipaddr_tuple(ip='11.0.0.1', port=123), status=psutil.CONN_ESTABLISHED, pid=11)

        t2 = net_connections_tuple(fd=115, family=socket.AF_INET, type=socket.SOCK_STREAM,
                                   laddr=ipaddr_tuple(ip='10.0.0.2', port=22222),
                                   raddr=ipaddr_tuple(ip='11.0.0.2', port=234), status=psutil.CONN_ESTABLISHED, pid=22)

        t3 = net_connections_tuple(fd=115, family=socket.AF_INET, type=socket.SOCK_STREAM,
                                   laddr=ipaddr_tuple(ip='10.0.0.3', port=33333),
                                   raddr=ipaddr_tuple(ip='11.0.0.3', port=345), status=psutil.CONN_ESTABLISHED, pid=33)

        t4 = net_connections_tuple(fd=115, family=socket.AF_INET, type=socket.SOCK_STREAM,
                                   laddr=ipaddr_tuple(ip='10.0.0.4', port=44444),
                                   raddr=ipaddr_tuple(ip='11.0.0.4', port=456), status=psutil.CONN_LISTEN, pid=44)

        t5 = net_connections_tuple(fd=115, family=socket.AF_INET, type=socket.SOCK_STREAM,
                                   laddr=ipaddr_tuple(ip='10.0.0.5', port=44444),
                                   raddr=ipaddr_tuple(ip='11.0.0.5', port=567), status=psutil.CONN_ESTABLISHED, pid=55)

        t6 = net_connections_tuple(fd=115, family=socket.AF_INET, type=socket.SOCK_DGRAM,
                                   laddr=ipaddr_tuple(ip='10.0.0.6', port=66666),
                                   raddr=ipaddr_tuple(ip='11.0.0.6', port=678), status=psutil.CONN_ESTABLISHED, pid=66)

        t7 = net_connections_tuple(fd=115, family=socket.AF_INET, type=socket.SOCK_DGRAM,
                                   laddr=ipaddr_tuple(ip='10.0.0.7', port=77777),
                                   raddr=ipaddr_tuple(ip='11.0.0.7', port=789), status=psutil.CONN_ESTABLISHED, pid=77)

        t8 = net_connections_tuple(fd=115, family=socket.AF_INET, type=socket.SOCK_DGRAM,
                                   laddr=ipaddr_tuple(ip='0.0.0.0', port=88888),
                                   raddr=ipaddr_tuple(ip='11.0.0.8', port=910), status=psutil.CONN_LISTEN, pid=88)

        array_of_temps = [t1, t2, t3, t4, t5, t6, t7, t8]
        return array_of_temps

    def __setup_if_addrs(self):
        a1 = if_addr_tuple(family=socket.AF_INET, address='10.0.0.1', netmask=None, broadcast=None, ptp=None)
        a2 = if_addr_tuple(family=socket.AF_INET, address='10.0.0.2', netmask=None, broadcast=None, ptp=None)
        a3 = if_addr_tuple(family=socket.AF_INET, address='10.0.0.3', netmask=None, broadcast=None, ptp=None)
        a4 = if_addr_tuple(family=socket.AF_INET, address='10.0.0.5', netmask=None, broadcast=None, ptp=None)
        a5 = if_addr_tuple(family=socket.AF_INET, address='10.0.0.6', netmask=None, broadcast=None, ptp=None)
        net_dict = {'em1': [a1, a2, a3, a4, a5]}
        return net_dict


    def test_collector_collect_network_stats(self):
        self.__use_mock_net_connections(self.__setup_net_connections())

        self.__use_mock_net_if_addrs(self.__setup_if_addrs())

        self.__use_mock_net_io_counters()
        self.mock_net_io_counters_result.bytes_recv = 10000
        self.mock_net_io_counters_result.bytes_sent = 20000
        self.mock_net_io_counters_result.packets_recv = 30000
        self.mock_net_io_counters_result.packets_sent = 40000

        new_collector = collector.Collector(short_metrics_names=False)
        metrics_output = new_collector.collect_metrics()

        assert metrics_output.network_stats['bytes_in'] == 10000
        assert metrics_output.network_stats['packets_in'] == 30000
        assert metrics_output.network_stats['bytes_out'] == 20000
        assert metrics_output.network_stats['packets_out'] == 40000

    def test_collector_listening_ports(self):

        self.__use_mock_net_connections(self.__setup_net_connections())

        self.__use_mock_net_if_addrs(self.__setup_if_addrs())

        self.__use_mock_net_io_counters()

        new_collector = collector.Collector(short_metrics_names=False)
        metrics_output = new_collector.collect_metrics()

        assert len(metrics_output.listening_ports('UDP')) == 3
        assert metrics_output.listening_ports('UDP')[0]['port'] == 66666
        assert metrics_output.listening_ports('UDP')[1]['port'] == 77777
        assert metrics_output.listening_ports('UDP')[2]['port'] == 88888

        assert len(metrics_output.listening_ports('TCP')) == 1
        assert metrics_output.listening_ports('TCP')[0]['port'] == 44444

    def test_collector_net_connections(self):
        self.__use_mock_net_connections(self.__setup_net_connections())

        self.__use_mock_net_if_addrs(self.__setup_if_addrs())

        self.__use_mock_net_io_counters()

        new_collector = collector.Collector(short_metrics_names=False)
        metrics_output = new_collector.collect_metrics()

        assert metrics_output.network_connections[0]['remote_addr'] == '11.0.0.1:123'
        assert metrics_output.network_connections[0]['local_interface'] == 'em1'
        assert metrics_output.network_connections[0]['local_port'] == 11111
        assert metrics_output.network_connections[1]['remote_addr'] == '11.0.0.2:234'
        assert metrics_output.network_connections[1]['local_interface'] == 'em1'
        assert metrics_output.network_connections[1]['local_port'] == 22222
        assert metrics_output.network_connections[2]['remote_addr'] == '11.0.0.3:345'
        assert metrics_output.network_connections[2]['local_interface'] == 'em1'
        assert metrics_output.network_connections[2]['local_port'] == 33333
        assert metrics_output.network_connections[3]['remote_addr'] == '11.0.0.5:567'
        assert metrics_output.network_connections[3]['local_interface'] == 'em1'
        assert metrics_output.network_connections[3]['local_port'] == 44444
        assert metrics_output.network_connections[4]['remote_addr'] == '11.0.0.6:678'
        assert metrics_output.network_connections[4]['local_interface'] == 'em1'
        assert metrics_output.network_connections[4]['local_port'] == 66666
        assert metrics_output.network_connections[5]['remote_addr'] == '11.0.0.7:789'
        assert metrics_output.network_connections[5]['local_interface'] is None
        assert metrics_output.network_connections[5]['local_port'] == 77777
