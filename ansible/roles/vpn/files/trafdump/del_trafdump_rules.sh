#!/bin/bash
# removes rules for traffic dump
# this script shouldn't be run normally :)

for chain in INPUT FORWARD OUTPUT; do
    iptables -t mangle -D $chain -s 10.80.0.0/14 -j TEE --gateway 10.10.10.6
    iptables -t mangle -D $chain -s 10.60.0.0/14 -j TEE --gateway 10.10.10.6
    iptables -t mangle -D $chain -s 10.10.10.2/32 -j TEE --gateway 10.10.10.6
    iptables -t mangle -D $chain -s 10.10.10.3/32 -j TEE --gateway 10.10.10.6
    iptables -t mangle -D $chain -s 10.10.10.4/32 -j TEE --gateway 10.10.10.6
    iptables -t mangle -D $chain -s 10.10.10.5/32 -j TEE --gateway 10.10.10.6
done
