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

r = s.get("/userRpm/SystemStatisticRpm.htm", params={"Num_per_page": 100})
root = lxml.html.fromstring(r.content)

stat_script = root.xpath("//script")[0].text
stat_json = stat_script.replace("var statList = new Array(", "[").replace(");", "]")
stat_list = json.loads(stat_json)

for row in iterutil.group(stat_list, 13):
    entry = StatsEntry(*row)
    print(entry)


r = s.get("/userRpm/AssignedIpAddrListRpm.htm")
root = lxml.html.fromstring(r.content)

dhcp_script = root.xpath("//script")[0].text
dhcp_json = dhcp_script.replace("var DHCPDynList = new Array(", "[").replace(");", "]")
dhcp_list = json.loads(dhcp_json)

for row in iterutil.group(dhcp_list, 4):
    entry = DHCPEntry(*row)
    print(entry)
