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


class Tags(object):
    """
    Abstract field name selection for metrics reports.
    """
    HEADER = ("header", "hed")
    METRICS = ("metrics", "met")
    REPORT_ID = ("report_id", "rid")
    VERSION = ("version", "v")
    TCP_CONN = ("tcp_connections", "tc")
    ESTABLISHED_CONNECTIONS = ("established_connections", "ec")
    CONNECTIONS = ("connections", "cs")
    REMOTE_ADDR = ("remote_addr", "rad")
    REMOTE_PORT = ("remote_port", "rp")
    LOCAL_PORT = ("local_port", "lp")
    LOCAL_INTERFACE = ("local_interface", "li")
    STATUS = ("status", "s")
    LISTENING_TCP_PORTS = ("listening_tcp_ports", "tp")
    LISTENING_UDP_PORTS = ("listening_udp_ports", "up")
    PORTS = ("ports", "pts")
    PORT = ("port", "pt")
    NETWORK_STATS = ("network_stats", "ns")
    BYTES_IN = ("bytes_in", "bi")
    BYTES_OUT = ("bytes_out", "bo")
    PACKETS_IN = ("packets_in", "pi")
    PACKETS_OUT = ("packets_out", "po")
    TOTAL = ("total", "t")

    def __init__(self, short_names=False):
        self.short_names = short_names

    def get(self, tag):
        if self.short_names:
            return tag[1]
        else:
            return tag[0]

    @property
    def header(self):
        return self.get(self.HEADER)

    @property
    def metrics(self):
        return self.get(self.METRICS)

    @property
    def report_id(self):
        return self.get(self.REPORT_ID)

    @property
    def version(self):
        return self.get(self.VERSION)

    @property
    def tcp_conn(self):
        return self.get(self.TCP_CONN)

    @property
    def connections(self):
        return self.get(self.CONNECTIONS)

    @property
    def established_connections(self):
        return self.get(self.ESTABLISHED_CONNECTIONS)

    @property
    def remote_addr(self):
        return self.get(self.REMOTE_ADDR)

    @property
    def remote_port(self):
        return self.get(self.REMOTE_PORT)

    @property
    def local_port(self):
        return self.get(self.LOCAL_PORT)

    @property
    def local_interface(self):
        return self.get(self.LOCAL_INTERFACE)

    @property
    def listening_tcp_ports(self):
        return self.get(self.LISTENING_TCP_PORTS)

    @property
    def listening_udp_ports(self):
        return self.get(self.LISTENING_UDP_PORTS)

    @property
    def ports(self):
        return self.get(self.PORTS)

    @property
    def interface_stats(self):
        return self.get(self.NETWORK_STATS)

    @property
    def interfaces(self):
        return self.get(self.INTERFACES)

    @property
    def bytes_in(self):
        return self.get(self.BYTES_IN)

    @property
    def bytes_out(self):
        return self.get(self.BYTES_OUT)

    @property
    def packets_in(self):
        return self.get(self.PACKETS_IN)

    @property
    def packets_out(self):
        return self.get(self.PACKETS_OUT)

    @property
    def total(self):
        return self.get(self.TOTAL)
