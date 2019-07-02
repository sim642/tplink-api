import io

from flask import send_file

from . import rrdtool_wrapper


def send_bytes(bytes, mimetype):
    return send_file(
        io.BytesIO(bytes),
        mimetype=mimetype
    )


def send_rrd_graph(*args):
    return send_bytes(
        rrdtool_wrapper.graph_return(*args),
        mimetype="image/png"
    )
