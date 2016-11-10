#!/bin/bash

# A helper script to show realtime team data in wireshark
# Uses ssh connection to traffic dump server

team="$1"

if [ -z $team ]; then
 echo "USAGE: ./get_realtime_team_traffic.sh <team_num>"
 exit
fi

net1="10.$((60 + team / 256)).$((team % 256)).0/24"
net2="10.$((80 + team / 256)).$((team % 256)).0/24"

filter="net ${net1} or net ${net2}"
ssh root@mon.a10 "tcpdump -U -i eth1 -w - -s 0 ${filter}" | wireshark -k -i -
