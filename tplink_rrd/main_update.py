import threading

import dotenv

from tplink import TpLinkApi
from .main_static import StaticBandwidthGenerator
from .rrds import BandwidthRrdTool
from .rrdtool_wrapper import LockRrdTool

dotenv.load_dotenv()

single_shot = False
generate_static = False

rrdtool = LockRrdTool()
rrds = BandwidthRrdTool(rrdtool)
generator = StaticBandwidthGenerator(rrdtool, rrds)

tplink = TpLinkApi.from_env()


def update(hostnames, stats):
    for entry in stats:
        hostname = hostnames.get(entry.ip)
        if hostname:
            rrds.update(hostname, entry.bytes_total)


def run():
    if not single_shot:
        threading.Timer(5, run).start()  # TODO: long interval

    stats = tplink.get_stats()
    dhcp = tplink.get_dhcp()
    hostnames = {entry.ip: entry.hostname for entry in dhcp}
    ips = {entry.hostname: entry.ip for entry in dhcp}

    update(hostnames, stats)

    if generate_static:
        generator.generate(ips)


run()
