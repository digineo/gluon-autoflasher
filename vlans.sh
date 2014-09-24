#!/bin/bash -e
# sudo apt-get install vlan

modprobe 8021q

interface=eth0
vlan_min=2
vlan_max=8
vlans=`seq $vlan_min $vlan_max`

case $1 in
  up)
    for vlan in $vlans; do
      iface=$interface.$vlan
      if [ ! -e /sys/class/net/$iface ]; then
        # add VLAN
        vconfig add $interface $vlan

        # wait for interface to appear
        sleep .1

        # add addresses and routes
        ip route flush table $vlan
        ip route add default table $vlan dev $iface
        for addr in 192.168.0.$vlan 192.168.1.$vlan; do
          ip addr add $addr/32 dev $iface
          ip rule add from $addr/32 table $vlan
        done
      fi
    done
    ip route flush cache
    ;;
  down)
    for vlan in $vlans; do
      iface=$interface.$vlan
      if [ -e /sys/class/net/$iface ]; then
        vconfig rem $iface
        ip route flush table $vlan
      fi
    done
    ;;
  *)
    echo "invalid command"
    ;;
esac

