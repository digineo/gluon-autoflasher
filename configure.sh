#!/bin/bash

hostname=$1
ssid=$2
key=$3

if [ -z "$hostname" ]; then
  echo no hostname given
  exit 1
fi

# fetch mac address
mac=$(arp -i eth0 -a 192.168.1.1 |grep -oE " [0-9a-f:]+ " |tr -d ' ')
if [ ${#mac} -ne  "17" ]; then
  echo could not fetch mac address
  exit 1
fi

# fetch mesh public key
mesh_key=`ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@192.168.1.1 /etc/init.d/fastd show_key mesh_vpn`
if [ -z "$mesh_key" ]; then
  echo could not fetch mesh key
  exit 1
fi

# set hostname, node info and enable mesh_vpn
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@192.168.1.1 <<EOF
  uci set system.@system[0].hostname="$hostname"
  uci set fastd.mesh_vpn.enabled=1
  uci get gluon-node-info.@owner[0] || uci add gluon-node-info owner
  uci set gluon-node-info.@owner[0].contact=jk+freifunk@digineo.de
  uci commit
EOF

# publish public key
curl -fsS -v "http://vpn.bremen.freifunk.net/newkey.php?mac=$mac&name=$hostname&key=$mesh_key"

# enable private wlan
if [ -n "$ssid" ]; then
  ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@192.168.1.1 <<EOF
    uci set wireless.wan_radio0=wifi-iface
    uci set wireless.wan_radio0.device=radio0
    uci set wireless.wan_radio0.network=wan
    uci set wireless.wan_radio0.mode=ap
    uci set wireless.wan_radio0.encryption=psk2
    uci set wireless.wan_radio0.ssid="$ssid"
    uci set wireless.wan_radio0.key="$key"
    uci set wireless.wan_radio0.disabled=0
    uci commit wireless
EOF
fi
