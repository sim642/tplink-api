import json
from typing import List
import os

import lxml.html
import requests_toolbelt.sessions

from .entries import *
from . import iterutil


class TpLinkApi:
    def __init__(self, address, username, password) -> None:
        super().__init__()

        self.session = requests_toolbelt.sessions.BaseUrlSession(base_url="http://" + address)
        self.session.auth = (username, password)

    @staticmethod
    def from_env():
        return TpLinkApi(
            os.getenv("TPLINK_ADDRESS"),
            os.getenv("TPLINK_USERNAME"),
            os.getenv("TPLINK_PASSWORD")
        )

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

    def get_stats(self, n=20, per_sec_interval=5) -> List[StatsEntry]:
        return self.list_to_entries(self.get_list("/userRpm/SystemStatisticRpm.htm", "statList", params={"interval": per_sec_interval, "Num_per_page": n}), 13, StatsEntry)

    def get_dhcp(self) -> List[DHCPEntry]:
        return self.list_to_entries(self.get_list("/userRpm/AssignedIpAddrListRpm.htm", "DHCPDynList"), 4, DHCPEntry)