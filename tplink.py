import json
from typing import NamedTuple, List

import lxml.html
import requests_toolbelt.sessions

import iterutil


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


class TpLinkApi:
    def __init__(self, address, username, password) -> None:
        super().__init__()

        self.session = requests_toolbelt.sessions.BaseUrlSession(base_url="http://" + address)
        self.session.auth = (username, password)

    def get_list(self, url, list_name, params=None):
        if params is None:
            params = {}
        r = self.session.get(url, params=params)
        root = lxml.html.fromstring(r.content)
        script = root.xpath("//script")[0].text
        list_json = script.replace(f"var {list_name} = new Array(", "[").replace(");", "]")
        return json.loads(list_json)

    @staticmethod
    def list_to_entries(iterable, n, typ):
        return [typ(*row) for row in iterutil.group(iterable, n)]

    def get_stats(self, interval, n=20) -> List[StatsEntry]:
        return self.list_to_entries(self.get_list("/userRpm/SystemStatisticRpm.htm", "statList", params={"interval": interval, "Num_per_page": n}), 13, StatsEntry)

    def get_dhcp(self) -> List[DHCPEntry]:
        return self.list_to_entries(self.get_list("/userRpm/AssignedIpAddrListRpm.htm", "DHCPDynList"), 4, DHCPEntry)
