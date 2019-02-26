import dotenv
import os

from tplink import TpLinkApi

dotenv.load_dotenv()


tplink = TpLinkApi(os.getenv("TPLINK_ADDRESS"), os.getenv("TPLINK_USERNAME"), os.getenv("TPLINK_PASSWORD"))

stats = tplink.get_stats(5)
dhcp = tplink.get_dhcp()
hostnames = {entry.ip: entry.hostname for entry in dhcp}

for entry in sorted(stats, key=lambda entry: entry.ip):
    hostname = hostnames.get(entry.ip)
    print(f"{entry.ip} ({hostname}): {entry.bytes_total} {entry.bytes_per_sec}")
