import math

import dotenv
import threading

from tplink import TpLinkApi
from .rrdtool_wrapper import LockRrdTool
from .rrds import BandwidthRrdTool
from .main_static import StaticBandwidthGenerator

dotenv.load_dotenv()

single_shot = False
generate_static = False

rrdtool = LockRrdTool()
rrds = BandwidthRrdTool(rrdtool)
generator = StaticBandwidthGenerator(rrdtool, rrds)

tplink = TpLinkApi.from_env()


def run():
    if not single_shot:
        threading.Timer(5, run).start()  # TODO: long interval

    stats = tplink.get_stats()
    dhcp = tplink.get_dhcp()
    hostnames = {entry.ip: entry.hostname for entry in dhcp}
    ips = {entry.hostname: entry.ip for entry in dhcp}

    def format_bytes(b):
        units = ["B", "kB", "MB", "GB", "TB"]
        i = math.floor(math.log(b, 1024)) if b > 0 else 0
        return f"{round(b / 1024 ** i * 100) / 100} {units[i]}"

    for entry in sorted(stats, key=lambda entry: entry.ip):
        hostname = hostnames.get(entry.ip)
        print(f"{entry.ip} ({hostname}): {format_bytes(entry.bytes_total)} {format_bytes(entry.bytes_per_sec)}/s")

        if hostname:
            rrds.update(hostname, entry.bytes_total)

    if generate_static:
        generator.generate(ips)


run()
