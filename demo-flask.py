import io
import os
import threading
import time

import dotenv
from flask import Flask, render_template, send_file

import rrds
import rrdtool_wrapper
from tplink import TpLinkApi

dotenv.load_dotenv()

app = Flask(__name__)

tplink = TpLinkApi(os.getenv("TPLINK_ADDRESS"), os.getenv("TPLINK_USERNAME"), os.getenv("TPLINK_PASSWORD"))

stats = None
hostnames = None


def tplink_thread():
    global stats, hostnames
    while True:
        stats = tplink.get_stats(5)  # TODO: longer interval here too?
        dhcp = tplink.get_dhcp()
        # print(dhcp)
        hostnames = {entry.ip: entry.hostname for entry in dhcp}

        time.sleep(5)  # TODO: much longer interval


t = threading.Thread(target=tplink_thread, daemon=True)
t.start()


@app.route("/")
def index():
    return render_template("graphs.html", hostnames=hostnames, stats=stats, starts=rrds.starts)


@app.route("/graph/<string:hostname>/<int:start>")
def graph_rrd(hostname, start):
    found_entry = None
    for entry in sorted(stats, key=lambda entry: entry.ip):
        entry_hostname = hostnames.get(entry.ip)
        if entry_hostname and entry_hostname == hostname:
            found_entry = entry

    image = rrdtool_wrapper.graph_return(rrds.graph_args(hostname, found_entry, start))
    return send_file(
        io.BytesIO(image),
        mimetype="image/png"
    )


@app.route("/graph-stack/<int:start>")
def graph_rrd_stack(start):
    image = rrdtool_wrapper.graph_return(rrds.graph_stack_args(hostnames, stats, start))
    return send_file(
        io.BytesIO(image),
        mimetype="image/png"
    )