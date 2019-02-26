import dotenv
import os
import requests_toolbelt.sessions
import lxml.html
import json
import iterutil

from typing import NamedTuple

dotenv.load_dotenv()


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


s = requests_toolbelt.sessions.BaseUrlSession(base_url="http://" + os.getenv("TPLINK_ADDRESS"))
s.auth = (os.getenv("TPLINK_USERNAME"), os.getenv("TPLINK_PASSWORD"))


def tplink_get_list(url, list_name, params=None):
    if params is None:
        params = {}
    r = s.get(url, params=params)
    root = lxml.html.fromstring(r.content)
    script = root.xpath("//script")[0].text
    list_json = script.replace("var {} = new Array(".format(list_name), "[").replace(");", "]")
    return json.loads(list_json)


def list_to_entries(list, n, typ):
    return [typ(*row) for row in iterutil.group(list, n)]


stat_entries = list_to_entries(tplink_get_list("/userRpm/SystemStatisticRpm.htm", "statList", params={"Num_per_page": 100}), 13, StatsEntry)
print(stat_entries)

dhcp_entries = list_to_entries(tplink_get_list("/userRpm/AssignedIpAddrListRpm.htm", "DHCPDynList"), 4, DHCPEntry)
print(dhcp_entries)