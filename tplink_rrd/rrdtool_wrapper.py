import rrdtool
import threading

rrdtool_lock = threading.Lock()


def graph_return(*args):
    with rrdtool_lock:
        return rrdtool.graphv("-", *args)["image"]


def graph_file(filename, *args):
    with rrdtool_lock:
        rrdtool.graph(filename, *args)


def create(filename, *args):
    with rrdtool_lock:
        rrdtool.create(filename, *args)