from pathlib import Path

import dotenv
from jinja2 import Environment, PackageLoader

from tplink import TpLinkApi
from .rrds import BandwidthRrdTool
from .rrdtool_wrapper import LockRrdTool


class StaticBandwidthGenerator:
    static_path = Path("static")
    graph_hostname_path = static_path / "graph-hostname"
    graph_stack_path = static_path / "graph-stack"

    def __init__(self, rrdtool, rrds) -> None:
        self.rrdtool = rrdtool
        self.rrds = rrds

        self.jinja2_env = Environment(loader=PackageLoader("tplink_rrd"))

    def generate_graph_hostname(self, hostname, ips, start):
        graph_path = self.graph_hostname_path / f"{hostname}-{start}.png"
        self.rrdtool.graph_file(
            graph_path,
            self.rrds.graph_args(hostname, ips.get(hostname), start)
        )

    def generate_graph_stack(self, sorted_hostnames, start):
        graph_path = self.graph_stack_path / f"{start}.png"
        self.rrdtool.graph_file(
            graph_path,
            self.rrds.graph_stack_args(sorted_hostnames, start)
        )

    def generate_index(self, sorted_hostnames):
        template = self.jinja2_env.get_template("graphs-static.html")
        template.stream(sorted_hostnames=sorted_hostnames, starts=self.rrds.starts).dump("static/index.html")

    def generate(self, ips):
        self.static_path.mkdir(exist_ok=True)
        self.graph_hostname_path.mkdir(exist_ok=True)
        self.graph_stack_path.mkdir(exist_ok=True)

        sorted_hostnames = self.rrds.get_sorted_hostnames(ips)

        for start in self.rrds.starts:
            self.generate_graph_stack(sorted_hostnames, start)

            for hostname in sorted_hostnames:
                self.generate_graph_hostname(hostname, ips, start)

        self.generate_index(sorted_hostnames)


if __name__ == '__main__':
    dotenv.load_dotenv()

    rrdtool = LockRrdTool()
    rrds = BandwidthRrdTool(rrdtool)
    generator = StaticBandwidthGenerator(rrdtool, rrds)

    tplink = TpLinkApi.from_env()

    dhcp = tplink.get_dhcp()
    ips = {entry.hostname: entry.ip for entry in dhcp}

    generator.generate(ips)
