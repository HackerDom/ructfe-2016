#!/bin/bash

trap 'echo -e "\nYou can rerun this script by /root/first_setup.sh"; exit' INT

echo RuCTFE 2016 Vulnbox Setup
echo

if ! ip link show eth0 &>/dev/null; then
 echo "Warning: you don't have an eth0 interface. This can cause troubles."
 echo
fi

read -p "Enter your team number: " TEAM

echo
echo "Change hostname"
echo "team${TEAM}.ructfe.org" > /etc/hostname
hostname team${TEAM}.ructfe.org

echo "Interface eth0 is your game network interface"
echo "Lets generate eth0 config."
echo "auto eth0" > /etc/network/interfaces.d/eth0.cfg
echo "iface eth0 inet static" >> /etc/network/interfaces.d/eth0.cfg
echo "address 10.$((60 + TEAM / 256)).$((TEAM % 256)).2" >>  /etc/network/interfaces.d/eth0.cfg
echo "netmask 255.255.255.0" >>  /etc/network/interfaces.d/eth0.cfg
echo "gateway 10.$((60 + TEAM / 256)).$((TEAM % 256)).1" >>  /etc/network/interfaces.d/eth0.cfg

echo "Here is your new /etc/network/interfaces.d/eth0.cfg:"
cat /etc/network/interfaces.d/eth0.cfg
echo

/etc/init.d/networking restart

echo
echo "Network configuration is over"

sed -i '/ONETIME/d' /root/.bashrc
