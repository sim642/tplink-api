import math

import dotenv
import os
import sqlite3

from tplink import TpLinkApi

dotenv.load_dotenv()


tplink = TpLinkApi(os.getenv("TPLINK_ADDRESS"), os.getenv("TPLINK_USERNAME"), os.getenv("TPLINK_PASSWORD"))

stats = tplink.get_stats(5)
dhcp = tplink.get_dhcp()
hostnames = {entry.ip: entry.hostname for entry in dhcp}


def format_bytes(b):
    units = ["B", "kB", "MB", "GB", "TB"]
    i = math.floor(math.log(b, 1024)) if b > 0 else 0
    return f"{round(b / 1024 ** i * 100) / 100} {units[i]}"


conn = sqlite3.connect("demo.sqlite")

for entry in sorted(stats, key=lambda entry: entry.ip):
    hostname = hostnames.get(entry.ip)
    print(f"{entry.ip} ({hostname}): {format_bytes(entry.bytes_total)} {format_bytes(entry.bytes_per_sec)}/s")

    if hostname:
        conn.execute(r"INSERT INTO demo(datetime, hostname, bytes) VALUES (datetime('now'), ?, ?)", (hostname, entry.bytes_total))

conn.commit()
conn.close()
