import io
import threading
import time

import dotenv
from flask import Flask, render_template, send_file

import rrds
import rrdtool_wrapper
from tplink import TpLinkApi

dotenv.load_dotenv()

app = Flask(__name__)

tplink = TpLinkApi.from_env()

stats = None
hostnames = None
ips = None


def tplink_thread():
    global stats, hostnames, ips
    while True:
        stats = tplink.get_stats(5)  # TODO: longer interval here too?
        dhcp = tplink.get_dhcp()
        # print(dhcp)
        hostnames = {entry.ip: entry.hostname for entry in dhcp}
        ips = {entry.hostname: entry.ip for entry in dhcp}

        time.sleep(5)  # TODO: much longer interval


def get_sorted_hostnames():
    sorted_hostnames = []
    for entry in sorted(stats, key=lambda entry: entry.ip):
        hostname = hostnames.get(entry.ip)
        if hostname:
            sorted_hostnames.append(hostname)
    return sorted_hostnames


t = threading.Thread(target=tplink_thread, daemon=True)
t.start()


@app.route("/")
def index():
    return render_template("graphs-flask.html", sorted_hostnames=get_sorted_hostnames(), starts=rrds.starts)


@app.route("/graph/<string:hostname>/<int:start>")
def graph_rrd(hostname, start):
    image = rrdtool_wrapper.graph_return(rrds.graph_args(hostname, ips[hostname], start))
    return send_file(
        io.BytesIO(image),
        mimetype="image/png"
    )


@app.route("/graph-stack/<int:start>")
def graph_rrd_stack(start):
    image = rrdtool_wrapper.graph_return(rrds.graph_stack_args(get_sorted_hostnames(), start))
    return send_file(
        io.BytesIO(image),
        mimetype="image/png"
    )