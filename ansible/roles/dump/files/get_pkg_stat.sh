#!/bin/bash

# Requires wireshark-common package

team="$1"
lastfiles=1000

if [ -z $team ]; then
 echo "USAGE: ./get_pkg_stat.sh <team_num>"
 exit
fi

teamdump=$(mktemp -d /home/dump/tmp.team${team}_XXXXX)
if [[ $? != 0 ]]; then
    exit 1
fi

if [ -z $teamdump ]; then
    exit 1
fi


cd /home/dump

net1="10.$((60 + team / 256)).$((team % 256)).0/24"
net2="10.$((80 + team / 256)).$((team % 256)).0/24"

c=0
for f in $(ls -t team*| head -${lastfiles}); do
    tcpdump -nr "$f" "net $net1 or net $net2" -w "${teamdump}/${c}" 2>/dev/null
    c=$((c + 1))
done

mergecap -F pcap -w "latest.team${team}.cap" ${teamdump}/*
rm -rf "${teamdump}"

getstat() {
    printf "%-6s:" "$1"
    n=$(tcpdump -Kqnr "latest.team${team}.cap" $2 2>/dev/null | wc -l)
    printf "%-6d " $n
    echo
}

getstat "All pkgs" ""
getstat "Icmp" "icmp"
getstat "Tcp" "tcp"
getstat "Udp" "udp"
echo "---"
getstat "Tcp:1111" "port 1111"
getstat "Tcp:2222" "port 2222"
getstat "Tcp:3333" "port 3333"
getstat "Tcp:4444" "port 4444"
getstat "Tcp:5555" "port 5555"
echo "---"
getstat "Checkers" "net 10.10.10.0/24"

for t in {0..256}; do
    n1="10.$((60 + t / 256)).$((t % 256)).0/24"
    n2="10.$((80 + t / 256)).$((t % 256)).0/24"

    getstat "Team $t" "net $n1 or $n2"
done
