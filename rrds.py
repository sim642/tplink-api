import colorutil
import os
import rrdtool_wrapper

HOSTNAME_WIDTH = 16


def ellipsize(s, length):
    return s[:length - 1] + '…' if len(s) > length else s


def hostname_rrd(hostname):
    filename = f"rrds/{hostname}.rrd"

    if not os.path.isfile(filename):
        rrdtool_wrapper.create(
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


starts = [
    3000,
    21000,
    93000,
    # 1147680,
]


def graph_args(hostname, ip, start):
    rrd = hostname_rrd(hostname)
    return [
        "--start", f"-{start}",
        "--title", f"{hostname} ({ip})",
        "--vertical-label", "bps",
        "--disable-rrdtool-tag",
        "--slope-mode",
        f"DEF:avgbytes={rrd}:bytes:AVERAGE",
        f"DEF:maxbytes={rrd}:bytes:MAX",
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
    ]


def graph_stack_args(sorted_hostnames, start):
    args = []
    for j, hostname in enumerate(sorted_hostnames):
        rrd = hostname_rrd(hostname)
        color = colorutil.rgb_to_hex(*colorutil.random_det(j))
        ellipsized_hostname = ellipsize(hostname, HOSTNAME_WIDTH)
        args += [
            f"DEF:avgbytes{j}={rrd}:bytes:AVERAGE",
            f"DEF:maxbytes{j}={rrd}:bytes:MAX",
            f"CDEF:avgbits{j}=avgbytes{j},8,*",
            f"CDEF:maxbits{j}=maxbytes{j},8,*",
            f"VDEF:totalavgbits{j}=avgbits{j},AVERAGE",
            f"VDEF:totalmaxbits{j}=maxbits{j},MAXIMUM",
            f"VDEF:totallastbits{j}=avgbits{j},LAST",
            f"AREA:avgbits{j}{color}:{ellipsized_hostname: <{HOSTNAME_WIDTH}}:STACK",
            # f"GPRINT:totalavgbits{j}:Average\\: %5.1lf %sbps",
            # f"GPRINT:totallastbits{j}:Current\\: %5.1lf %sbps\\n",
            f"GPRINT:totalavgbits{j}:%7.1lf %sbps",
            f"GPRINT:totalmaxbits{j}:%7.1lf %sbps",
            f"GPRINT:totallastbits{j}:%7.1lf %sbps\\n",
        ]

    return [
        "--start", f"-{start}",
        # "--title", f"{hostname} ({entry.ip})",
        "--vertical-label", "bps",
        "--disable-rrdtool-tag",
        "--slope-mode",
        "--height", "150",  # default is 100
        f"COMMENT:{'': <{HOSTNAME_WIDTH + 2}}",
        f"COMMENT:{'Average': ^12}",
        f"COMMENT:{'Max': ^12}",
        f"COMMENT:{'Current': ^12}\\n",
    ] + args