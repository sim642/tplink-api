Python library for older TP-Link routers with `userRpm` API.
Includes an application for graphing per-device traffic statistics using [rrdtool].

[rrdtool]: http://oss.oetiker.ch/rrdtool/

> [!WARNING]
> Not compatible with newer TP-Link (mesh) routers.


# TP-Link reverse engineering
The following is a list of notes and resources related to reverse engineering of TP-Link routers and their APIs.

* `userRpm` API:
  * HTTP access via web interface
  * HTTP auth
  * `/userRpm/` URLs
  * Parse array in `<script>` tag to extract results
  * Implementations:
    * _This repository_
    * https://github.com/n1k0r/tplink-wr-api
    * https://github.com/mkubicek/tpylink
    * Prometheus exporter: https://github.com/maesoser/tplink_exporter
* `seq` API:
  * HTTP access via web interface
  * HTTP auth
  * Custom protocol with some kind of sequences
  * Implementations:
    * https://github.com/menahishayan/TP-Link-Archer-C50-API/
    * https://github.com/epsi95/TPLink-Python
    * https://github.com/AlexandrErohin/TP-Link-Archer-C6U (`TPLinkMRClient`)
    * Home-assistant integration: https://github.com/ericpignet/home-assistant-tplink_router/tree/master
    * https://github.com/hertzg/node-tplink-api
* `luci` API:
  * HTTP access via web interface
  * Custom auth with RSA and cookies
  * Only one simultaneous user, kicks out others
  * `/cgi-bin/luci/` URLs
  * Implementations:
    * https://github.com/AlexandrErohin/TP-Link-Archer-C6U
      * Home-assistant integration: https://github.com/AlexandrErohin/home-assistant-tplink-router
* Reverse engineering:
  * https://skowronski.tech/2021/02/hacking-into-tp-link-archer-c6-shell-access-without-physical-disassembly/
  * https://github.com/hacefresko/TP-Link-Archer-C6-EU-re 
