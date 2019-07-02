from typing import NamedTuple


class StatsEntry(NamedTuple):
    id: int
    ip: str
    mac: str
    packets_total: int
    bytes_total: int
    packets_per_sec: int
    bytes_per_sec: int
    icmp_per_sec: int
    icmp_per_sec_max: int
    udp_per_sec: int
    udp_per_sec_max: int
    tcp_syn_per_sec: int
    tcp_syn_per_sec_max: int


class DHCPEntry(NamedTuple):
    hostname: str
    mac: str
    ip: str
    lease_time: str