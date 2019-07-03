import math

import dotenv
import os
import threading

from tplink import TpLinkApi
from .rrdtool_wrapper import LockRrdTool
from .rrds import BandwidthRrdTool
from jinja2 import Environment, PackageLoader

dotenv.load_dotenv()

single_shot = False
generate_static = False

rrdtool = LockRrdTool()
rrds = BandwidthRrdTool(rrdtool)

jinja2_env = Environment(loader=PackageLoader("tplink_rrd", "templates"))


def graph_rrd(hostname, entry):
    for start in rrds.starts:
        graph_filename = f"graphs/{hostname}-{start}.png"
        rrdtool.graph_file(
            graph_filename,
            rrds.graph_args(hostname, entry.ip, start)
        )


def get_sorted_hostnames(hostnames, stats):
    sorted_hostnames = []
    for entry in sorted(stats, key=lambda entry: entry.ip):
        hostname = hostnames.get(entry.ip)
        if hostname:
            sorted_hostnames.append(hostname)
    return sorted_hostnames


def graph_rrd_stack(hostnames, stats):
    sorted_hostnames = get_sorted_hostnames(hostnames, stats)
    for start in rrds.starts:
        graph_filename = f"graphs/stack-{start}.png"
        rrdtool.graph_file(
            graph_filename,
            rrds.graph_stack_args(sorted_hostnames, start)
        )


def graphs_index(hostnames, stats):
    sorted_hostnames = get_sorted_hostnames(hostnames, stats)
    template = jinja2_env.get_template("graphs-static.html")
    template.stream(sorted_hostnames=sorted_hostnames, starts=rrds.starts).dump("graphs/index.html")


tplink = TpLinkApi.from_env()

if generate_static:
    os.makedirs("graphs", exist_ok=True)


def run():
    if not single_shot:
        threading.Timer(5, run).start()  # TODO: long interval

    stats = tplink.get_stats()
    dhcp = tplink.get_dhcp()
    hostnames = {entry.ip: entry.hostname for entry in dhcp}

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
                graph_rrd(hostname, entry)

    if generate_static:
        graph_rrd_stack(hostnames, stats)
        graphs_index(hostnames, stats)


run()
