import threading
import time

import dotenv
from flask import Flask, render_template

from tplink import TpLinkApi
from .flaskutil import send_bytes
from .rrds import BandwidthRrdTool
from .rrdtool_wrapper import MultiprocessRrdTool

dotenv.load_dotenv()

app = Flask(__name__)

rrdtool = MultiprocessRrdTool()
rrds = BandwidthRrdTool(rrdtool)


def send_rrd_graph(*args):
    return send_bytes(
        rrdtool.graph_return(*args),
        mimetype="image/png"
    )


tplink = TpLinkApi.from_env()

stats = None
hostnames = None
ips = None


def tplink_thread():
    global stats, hostnames, ips
    while True:
        stats = tplink.get_stats()
        dhcp = tplink.get_dhcp()
        # print(dhcp)
        hostnames = {entry.ip: entry.hostname for entry in dhcp}
        ips = {entry.hostname: entry.ip for entry in dhcp}

        time.sleep(5)  # TODO: much longer interval


def get_sorted_hostnames():
    return rrds.get_sorted_hostnames(ips)


t = threading.Thread(target=tplink_thread, daemon=True)
t.start()


@app.route("/")
def index():
    return render_template("graphs-flask.html", sorted_hostnames=get_sorted_hostnames(), starts=rrds.starts)


@app.route("/graph/<string:hostname>/<int:start>")
def graph_rrd(hostname, start):
    return send_rrd_graph(rrds.graph_args(hostname, ips.get(hostname), start))


@app.route("/graph-stack/<int:start>")
def graph_rrd_stack(start):
    return send_rrd_graph(rrds.graph_stack_args(get_sorted_hostnames(), start))