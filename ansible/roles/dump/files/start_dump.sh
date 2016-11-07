#!/bin/bash

# A helper script to show realtime team data in wireshark
# Uses ssh connection to traffic dump server

team="$1"

if [ -z $team ]; then
 echo "USAGE: ./start_dump.sh <team_num>"
 exit
fi

net1="10.$((60 + team / 256)).$((team % 256)).0/24"
net2="10.$((80 + team / 256)).$((team % 256)).0/24"

filter="net ${net1} or net ${net2}"
exec tcpdump -U -i eth1 -C 20 -w "/home/dump/team${team}" -s 0 "${filter}"
