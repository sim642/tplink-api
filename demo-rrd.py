import math

import dotenv
import os
import rrdtool
import time
import colorsys

from tplink import TpLinkApi

dotenv.load_dotenv()


os.makedirs("rrds", exist_ok=True)
os.makedirs("graphs", exist_ok=True)


def get_rrd(hostname):
    filename = f"rrds/{hostname}.rrd"

    if not os.path.isfile(filename):
        rrdtool.create(
            filename,
            "--start", "now",
            "--step", "5",  # TODO: 5 minutes (300s) instead of 5 seconds
            "DS:bytes:COUNTER:10:U:U",  # TODO: 10 minutes (600s) instead of 10 seconds
            "RRA:AVERAGE:0.5:1:600",
            "RRA:AVERAGE:0.5:6:700",
            "RRA:AVERAGE:0.5:24:775",
            "RRA:AVERAGE:0.5:288:797",
            "RRA:MAX:0.5:1:600",
            "RRA:MAX:0.5:6:700",
            "RRA:MAX:0.5:24:775",
            "RRA:MAX:0.5:288:797",
        )

    return filename

def update_rrd(hostname, bytes_total):
    filename = get_rrd(hostname)
    rrdtool.update(filename, f"N:{bytes_total}")

graphs = [
    "-3000",
    "-21000",
    "-93000",
    # "-1147680",
]

def graph_rrd(hostname, entry):
    rrd_filename = get_rrd(hostname)

    for i, start in enumerate(graphs):
        graph_filename = f"graphs/{hostname}-{i}.png"

        rrdtool.graph(
            graph_filename,
            "--start", start,  # TODO: proper beginning time
            "--title", f"{hostname} ({entry.ip})",
            "--vertical-label", "bps",
            "--disable-rrdtool-tag",
            "--slope-mode",
            f"DEF:avgbytes={rrd_filename}:bytes:AVERAGE",
            f"DEF:maxbytes={rrd_filename}:bytes:MAX",
            "CDEF:avgbits=avgbytes,8,*",
            "CDEF:maxbits=maxbytes,8,*",
            "VDEF:totalavgbits=avgbits,AVERAGE",
            "VDEF:totalmaxbits=maxbits,MAXIMUM",
            "VDEF:totallastbits=avgbits,LAST",
            "AREA:avgbits#00FF00:Average",
            # "GPRINT:totalavgbits:Average\\: %.1lf %sbps",
            "GPRINT:totalavgbits:%.1lf %sbps",
            "LINE0.5:maxbits#FF0000:Max",
            # "GPRINT:totalmaxbits:Max\\: %.1lf %sbps",
            "GPRINT:totalmaxbits:%.1lf %sbps",
            "COMMENT:Current",
            "GPRINT:totallastbits:%.1lf %sbps\\n",
        )

def graph_rrd_stack(hostnames, stats):
    def color(j):
        # https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
        h, s, v = (0.618033988749895 * j) % 1, 1, 1
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"

    for i, start in enumerate(graphs):
        graph_filename = f"graphs/stack-{i}.png"

        args = []
        j = 0
        for entry in sorted(stats, key=lambda entry: entry.ip):
            hostname = hostnames.get(entry.ip)
            if hostname:
                args += [
                    f"DEF:avgbytes{j}={get_rrd(hostname)}:bytes:AVERAGE",
                    f"DEF:maxbytes{j}={get_rrd(hostname)}:bytes:MAX",
                    f"CDEF:avgbits{j}=avgbytes{j},8,*",
                    f"CDEF:maxbits{j}=maxbytes{j},8,*",
                    f"VDEF:totalavgbits{j}=avgbits{j},AVERAGE",
                    f"VDEF:totalmaxbits{j}=maxbits{j},MAXIMUM",
                    f"VDEF:totallastbits{j}=avgbits{j},LAST",
                    f"AREA:avgbits{j}{color(j)}:{hostname: <16}:STACK",
                    # f"GPRINT:totalavgbits{j}:Average\\: %5.1lf %sbps",
                    # f"GPRINT:totallastbits{j}:Current\\: %5.1lf %sbps\\n",
                    f"GPRINT:totalavgbits{j}:%7.1lf %sbps",
                    f"GPRINT:totalmaxbits{j}:%7.1lf %sbps",
                    f"GPRINT:totallastbits{j}:%7.1lf %sbps\\n",
                ]

                j += 1

        rrdtool.graph(
            graph_filename,
            "--start", start,  # TODO: proper beginning time
            # "--title", f"{hostname} ({entry.ip})",
            "--vertical-label", "bps",
            "--disable-rrdtool-tag",
            "--slope-mode",
            "--height", "150", # default is 100
            f"COMMENT:{'': <18}",
            f"COMMENT:{'Average': ^12}",
            f"COMMENT:{'Max': ^12}",
            f"COMMENT:{'Current': ^12}\\n",
            *args
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

        for i in reversed(range(len(graphs))):
            index_file.write(
                f"<img src=\"stack-{i}.png\" />"
            )

        index_file.write("<hr />")

        for entry in sorted(stats, key=lambda entry: entry.ip):
            hostname = hostnames.get(entry.ip)
            if hostname:
                for i in reversed(range(len(graphs))):
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
