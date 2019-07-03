import os

import dotenv
from jinja2 import Environment, PackageLoader

from tplink import TpLinkApi
from .rrds import BandwidthRrdTool
from .rrdtool_wrapper import LockRrdTool


class StaticBandwidthGenerator:
    def __init__(self, rrdtool, rrds) -> None:
        self.rrdtool = rrdtool
        self.rrds = rrds

        self.jinja2_env = Environment(loader=PackageLoader("tplink_rrd", "templates"))

    def graph_rrd(self, hostname, ips):
        for start in self.rrds.starts:
            graph_filename = f"graphs/{hostname}-{start}.png"
            self.rrdtool.graph_file(
                graph_filename,
                self.rrds.graph_args(hostname, ips.get(hostname), start)
            )

    def graph_rrd_stack(self, ips):
        sorted_hostnames = self.rrds.get_sorted_hostnames(ips)
        for start in self.rrds.starts:
            graph_filename = f"graphs/stack-{start}.png"
            self.rrdtool.graph_file(
                graph_filename,
                self.rrds.graph_stack_args(sorted_hostnames, start)
            )

    def graphs_index(self, ips):
        sorted_hostnames = self.rrds.get_sorted_hostnames(ips)
        template = self.jinja2_env.get_template("graphs-static.html")
        template.stream(sorted_hostnames=sorted_hostnames, starts=self.rrds.starts).dump("graphs/index.html")

    def generate(self, ips):
        os.makedirs("graphs", exist_ok=True)

        for hostname in self.rrds.get_sorted_hostnames(ips):
            self.graph_rrd(hostname, ips)

        self.graph_rrd_stack(ips)
        self.graphs_index(ips)


if __name__ == '__main__':
    dotenv.load_dotenv()

    rrdtool = LockRrdTool()
    rrds = BandwidthRrdTool(rrdtool)
    generator = StaticBandwidthGenerator(rrdtool, rrds)

    tplink = TpLinkApi.from_env()

    dhcp = tplink.get_dhcp()
    ips = {entry.hostname: entry.ip for entry in dhcp}

    generator.generate(ips)
