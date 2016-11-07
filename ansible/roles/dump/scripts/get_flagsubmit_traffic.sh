#!/bin/bash

# A helper script to show realtime team data in wireshark
# Uses ssh connection to traffic dump server

filter="port 31337"
ssh root@mon.a10 "tcpdump -U -i eth1 -w - -s 0 ${filter}" | wireshark -k -i -
