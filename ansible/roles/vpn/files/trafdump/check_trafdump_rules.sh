#!/bin/bash
# checks rules for teams snat. Team will see incoming connections from 10.8{0..3}.{0..254}.1
# this script should be run once before the game starts

for chain in INPUT FORWARD OUTPUT; do
    echo "$chain chain:"
    if ! iptables -t mangle -C $chain -s 10.80.0.0/14 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        echo " 10.80.0.0/14 rule is OFF"
    else
        echo " 10.80.0.0/14 rule is ON"
    fi

    if ! iptables -t mangle -C $chain -s 10.60.0.0/14 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        echo " 10.60.0.0/14 rule is OFF"
    else
        echo " 10.60.0.0/14 rule is ON"
    fi

    if ! iptables -t mangle -C $chain -s 10.10.10.2/32 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        echo " 10.10.10.2/32 rule is OFF"
    else
        echo " 10.10.10.2/32 rule is ON"
    fi

    if ! iptables -t mangle -C $chain -s 10.10.10.3/32 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        echo " 10.10.10.3/32 rule is OFF"
    else
        echo " 10.10.10.3/32 rule is ON"
    fi

    if ! iptables -t mangle -C $chain -s 10.10.10.4/32 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        echo " 10.10.10.4/32 rule is OFF"
    else
        echo " 10.10.10.4/32 rule is ON"
    fi

    if ! iptables -t mangle -C $chain -s 10.10.10.5/32 -j TEE --gateway 10.10.10.6 &>/dev/null; then
        echo " 10.10.10.5/32 rule is OFF"
    else
        echo " 10.10.10.5/32 rule is ON"
    fi
done
