import math

import dotenv
import os
import rrdtool
import time

from tplink import TpLinkApi
import rrdtool_wrapper
import rrds

dotenv.load_dotenv()


os.makedirs("rrds", exist_ok=True)
os.makedirs("graphs", exist_ok=True)

def update_rrd(hostname, bytes_total):
    filename = rrds.hostname_rrd(hostname)
    rrdtool.update(filename, f"N:{bytes_total}")


def graph_rrd(hostname, entry):
    for i, start in enumerate(rrds.starts):
        graph_filename = f"graphs/{hostname}-{i}.png"
        rrdtool_wrapper.graph_file(
            graph_filename,
            rrds.graph_args(hostname, entry.ip, start)
        )

def graph_rrd_stack(hostnames, stats):
    sorted_hostnames = []
    for entry in sorted(stats, key=lambda entry: entry.ip):
        hostname = hostnames.get(entry.ip)
        if hostname:
            sorted_hostnames.append(hostname)

    for i, start in enumerate(rrds.starts):
        graph_filename = f"graphs/stack-{i}.png"
        rrdtool_wrapper.graph_file(
            graph_filename,
            rrds.graph_stack_args(sorted_hostnames, start)
        )

def graphs_index(hostnames, stats):
    with open("graphs/index.html", "w") as index_file:
        index_file.write(
"""<!DOCTYPE html>
<html>
<head>
    <title>tplink-api graphs</title>
    <meta http-equiv="refresh" content="5">
</head>
<body>""")

        for i in reversed(range(len(rrds.starts))):
            index_file.write(
                f"<img src=\"stack-{i}.png\" />"
            )

        index_file.write("<hr />")

        for entry in sorted(stats, key=lambda entry: entry.ip):
            hostname = hostnames.get(entry.ip)
            if hostname:
                for i in reversed(range(len(rrds.starts))):
                    index_file.write(
                        f"<img src=\"{hostname}-{i}.png\" />"
                    )

                index_file.write("<br />")

        index_file.write(
"""</body>
</html>""")


tplink = TpLinkApi(os.getenv("TPLINK_ADDRESS"), os.getenv("TPLINK_USERNAME"), os.getenv("TPLINK_PASSWORD"))


while True:
    stats = tplink.get_stats(5)  # TODO: longer interval here too?
    dhcp = tplink.get_dhcp()
    # print(dhcp)
    hostnames = {entry.ip: entry.hostname for entry in dhcp}


    def format_bytes(b):
        units = ["B", "kB", "MB", "GB", "TB"]
        i = math.floor(math.log(b, 1024)) if b > 0 else 0
        return f"{round(b / 1024 ** i * 100) / 100} {units[i]}"


    for entry in sorted(stats, key=lambda entry: entry.ip):
        hostname = hostnames.get(entry.ip)
        print(f"{entry.ip} ({hostname}): {format_bytes(entry.bytes_total)} {format_bytes(entry.bytes_per_sec)}/s")

        if hostname:
            update_rrd(hostname, entry.bytes_total)
            graph_rrd(hostname, entry)

    graph_rrd_stack(hostnames, stats)
    graphs_index(hostnames, stats)

    time.sleep(5)  # TODO: long interval
