import dotenv
import os

from tplink import TpLinkApi

dotenv.load_dotenv()


tplink = TpLinkApi(os.getenv("TPLINK_ADDRESS"), os.getenv("TPLINK_USERNAME"), os.getenv("TPLINK_PASSWORD"))

print(tplink.get_stats())
print(tplink.get_dhcp())