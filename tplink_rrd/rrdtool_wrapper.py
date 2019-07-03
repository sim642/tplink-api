import rrdtool
import threading
import multiprocessing


def graph_return(*args):
    return rrdtool.graphv("-", *args)["image"]


def graph_file(filename, *args):
        rrdtool.graph(filename, *args)


# librrdtool isn't thread safe:
# https://oss.oetiker.ch/rrdtool/prog/rrdthreads.en.html
#
# concurrent graph produces broken graphs when called from Flask threads

class LockRrdTool:
    def __init__(self) -> None:
        self.lock = threading.Lock()

    def graph_return(self, *args):
        with self.lock:
            return graph_return(*args)

    def graph_file(self, filename, *args):
        with self.lock:
            graph_file(filename, *args)

    def create(self, filename, *args):
        with self.lock:
            rrdtool.create(filename, *args)

    def update(self, filename, *args):
        with self.lock:
            rrdtool.update(filename, *args)


class MultiprocessRrdTool(LockRrdTool):
    def __init__(self) -> None:
        super().__init__()

        self.pool = multiprocessing.Pool()

    def graph_return(self, *args):
        return self.pool.apply(graph_return, args=args)

    def graph_file(self, filename, *args):
        self.pool.apply(graph_file, args=(filename, *args))