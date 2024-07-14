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
    * https://github.com/plewin/tp-link-modem-router
    * https://github.com/hercule115/TPLink-Archer
* `luci` API:
  * HTTP access via web interface
  * Custom auth with RSA and cookies
  * Only one simultaneous user, kicks out others
  * `/cgi-bin/luci/` URLs
  * Implementations:
    * https://github.com/AlexandrErohin/TP-Link-Archer-C6U
      * Home-assistant integration: https://github.com/AlexandrErohin/home-assistant-tplink-router
* TMP API:
  * TP-Link Tether 2.0 protocol for mobile app
  * Multiple transports (SSH, BLE, ATA) according to Android app decompile
    * SSH:
      * User: `dropbear`, password: `admin`/own password (for web interface)
      * No `shell` channel
      * Android app uses `exec` channel for `scp`
      * Port forward 20002 to access TMP
  * Versions 1, 2, 3 according to Android app decompile 
  * Reverse engineering:
    * https://www.zerodayinitiative.com/blog/2020/4/6/exploiting-the-tp-link-archer-c7-at-pwn2own-tokyo
    * https://labs.withsecure.com/advisories/tp-link-ac1750-pwn2own-2019
  * Implementations:
    * https://github.com/ropbear/tmpcli
* TDDP API?
  * https://mjg59.dreamwidth.org/51672.html 
* Reverse engineering:
  * https://skowronski.tech/2021/02/hacking-into-tp-link-archer-c6-shell-access-without-physical-disassembly/
  * https://github.com/hacefresko/TP-Link-Archer-C6-EU-re
