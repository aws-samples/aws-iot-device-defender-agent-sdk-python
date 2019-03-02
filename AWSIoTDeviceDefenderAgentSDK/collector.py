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


import psutil as ps
import socket
from AWSIoTDeviceDefenderAgentSDK import metrics
import argparse
from time import sleep


class Collector(object):
    """
    Reads system information and populates a metrics object.

    This implementation utilizes `psutil <https://psutil.readthedocs.io/en/latest/>`_
    to make parsing metrics easier and more cross-platform.
    """

    def __init__(self, short_metrics_names=False):
        """
        Parameters
        ----------
        short_metrics_names : bool
                Toggle short object tags in output metrics.
        """

        # Keep a copy of the last metric, if there is one, so we can calculate change in some metrics.
        self._last_metric = None
        self._short_names = short_metrics_names

    @staticmethod
    def __get_interface_name(address):

        if address == '0.0.0.0' or address == '::':
            return address

        for iface in ps.net_if_addrs():
            for snic in ps.net_if_addrs()[iface]:
                if snic.address == address:
                    return iface

    def listening_ports(self, metrics):
        """
        Iterate over all inet connections in the LISTEN state and extract port and interface.
        """
        udp_ports = []
        tcp_ports = []
        for conn in ps.net_connections(kind='inet'):
            iface = Collector.__get_interface_name(conn.laddr.ip)
            if conn.status == "LISTEN" and conn.type == socket.SOCK_STREAM:
                if iface:
                    tcp_ports.append({'port': conn.laddr.port, 'interface': iface})
                else:
                    tcp_ports.append({'port': conn.laddr.port})
            if conn.type == socket.SOCK_DGRAM:  # on Linux, udp socket status is always "NONE"
                if iface:
                    udp_ports.append({'port': conn.laddr.port, 'interface': iface})
                else:
                    udp_ports.append({'port': conn.laddr.port})

        metrics.add_listening_ports("UDP", udp_ports)
        metrics.add_listening_ports("TCP", tcp_ports)

    @staticmethod
    def network_stats(metrics):
        net_counters = ps.net_io_counters(pernic=False)
        metrics.add_network_stats(
            net_counters.bytes_recv,
            net_counters.packets_recv,
            net_counters.bytes_sent,
            net_counters.packets_sent)

    @staticmethod
    def network_connections(metrics):
        protocols = ['tcp']
        for protocol in protocols:
            for c in ps.net_connections(kind=protocol):
                try:
                    if c.status == "ESTABLISHED" or c.status == "BOUND":
                        metrics.add_network_connection(c.raddr.ip, c.raddr.port,
                                                       Collector.__get_interface_name(c.laddr.ip),
                                                       c.laddr.port)
                except Exception as ex:
                    print('Failed to parse network info for protocol: ' + protocol)
                    print(ex)

    def collect_metrics(self):
        """Sample system metrics and populate a metrics object suitable for publishing to Device Defender."""
        metrics_current = metrics.Metrics(
            short_names=self._short_names, last_metric=self._last_metric)

        self.network_stats(metrics_current)
        self.listening_ports(metrics_current)
        self.network_connections(metrics_current)

        self._last_metric = metrics_current
        return metrics_current


def main():
    """Use this method to run the collector in stand-alone mode to tests metric collection."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sample_rate", action="store", dest="sample_rate", required=False,
                        help="Interval between individual samples, cannot exceed Upload Rate")
    parser.add_argument("-n", "--number_samples", action="store", dest="number_samples", default=0, required=False,
                        help="Number of samples to collect before exiting")
    parser.add_argument("-l", "--list_size", action="store",
                        dest="max_list_size", default=None, required=False,
                        help="Lists larger than this size will be sampled")
    parser.add_argument("--short-names", action="store_true", dest="short_names", default=False, required=False,
                        help="Produce metric report with short names")

    args = parser.parse_args()
    collector = Collector(short_metrics_names=args.short_names)

    if args.sample_rate:
        count = int(args.number_samples)
        while True:
            count -= 1
            # setup a loop to collect
            metric = collector.collect_metrics()
            print(metric.to_json_string(pretty_print=True))

            if count == 0:
                break

            sleep(float(args.sample_rate))

    else:
        metric = collector.collect_metrics()

        if args.max_list_size:
            metric.max_list_size = int(args.max_list_size)

        print(metric.to_json_string(pretty_print=True))
        exit()


if __name__ == '__main__':
    main()
