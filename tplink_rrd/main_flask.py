import threading
import time

import dotenv
from flask import Flask, render_template, request

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
ips = {}
sorted_hostnames = []


def tplink_thread():
    global ips, sorted_hostnames
    while True:
        dhcp = tplink.get_dhcp()
        ips = {entry.hostname: entry.ip for entry in dhcp}
        sorted_hostnames = rrds.get_sorted_hostnames(ips)

        time.sleep(5)  # TODO: much longer interval


t = threading.Thread(target=tplink_thread, daemon=True)
t.start()


@app.route("/")
def index():
    return render_template("graphs-flask.html", sorted_hostnames=sorted_hostnames, starts=rrds.starts)


@app.route("/graph/hostname/<string:hostname>")
def graph_hostname(hostname):
    start = request.args.get("start")
    return send_rrd_graph(rrds.graph_args(hostname, ips.get(hostname), start))


@app.route("/graph/stack")
def graph_stack():
    start = request.args.get("start")
    return send_rrd_graph(rrds.graph_stack_args(sorted_hostnames, start))