import dotenv
import os
import requests_toolbelt.sessions
import lxml.html
import json
import iterutil

dotenv.load_dotenv()

s = requests_toolbelt.sessions.BaseUrlSession(base_url="http://" + os.getenv("TPLINK_ADDRESS"))
s.auth = (os.getenv("TPLINK_USERNAME"), os.getenv("TPLINK_PASSWORD"))

r = s.get("/userRpm/SystemStatisticRpm.htm", params={"Num_per_page": 100})
root = lxml.html.fromstring(r.content)

stat_script = root.xpath("//script")[0].text
stat_json = stat_script.replace("var statList = new Array(", "[").replace(");", "]")
stat_list = json.loads(stat_json)

for row in iterutil.group(stat_list, 13):
    print(row)


r = s.get("/userRpm/AssignedIpAddrListRpm.htm")
root = lxml.html.fromstring(r.content)

dhcp_script = root.xpath("//script")[0].text
dhcp_json = dhcp_script.replace("var DHCPDynList = new Array(", "[").replace(");", "]")
dhcp_list = json.loads(dhcp_json)

for row in iterutil.group(dhcp_list, 4):
    print(row)
