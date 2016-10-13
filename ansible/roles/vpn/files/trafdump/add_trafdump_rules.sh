#!/bin/bash
# adds rules for traffic dump
# this script should be run once before the game starts

for chain in INPUT FORWARD OUTPUT; do
    if ! iptables -t mangle -C $chain -s 10.80.0.0/14 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        iptables -t mangle -A $chain -s 10.80.0.0/14 -j TEE --gateway 10.10.10.6
    fi

    if ! iptables -t mangle -C $chain -s 10.60.0.0/14 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        iptables -t mangle -A $chain -s 10.60.0.0/14 -j TEE --gateway 10.10.10.6
    fi

    if ! iptables -t mangle -C $chain -s 10.10.10.2/32 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        iptables -t mangle -A $chain -s 10.10.10.2/32 -j TEE --gateway 10.10.10.6
    fi

    if ! iptables -t mangle -C $chain -s 10.10.10.3/32 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        iptables -t mangle -A $chain -s 10.10.10.3/32 -j TEE --gateway 10.10.10.6
    fi

    if ! iptables -t mangle -C $chain -s 10.10.10.4/32 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        iptables -t mangle -A $chain -s 10.10.10.4/32 -j TEE --gateway 10.10.10.6
    fi

    if ! iptables -t mangle -C $chain -s 10.10.10.5/32 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        iptables -t mangle -A $chain -s 10.10.10.5/32 -j TEE --gateway 10.10.10.6
    fi
done
