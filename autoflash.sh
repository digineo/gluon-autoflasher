#!/bin/bash

source ./config

function quit() {
	if [ x"${BASH_SOURCE[0]}" == x"$0" ]; then
		exit $*
	else
		return $*
	fi
}

function curl_admin() {
	curl -fsS --basic -u admin:admin $@
}

if [ ! -e downloads.openwrt.org ]; then
	# download missing firmware images
  ./download_images.sh || quit 1
fi

ping -n -c 1 -W 1 192.168.0.1 > /dev/null
if [ $? -ne 0 ]; then
	echo "ROUTER OFFLINE? cannot ping 192.168.0.1 :("
	quit 2
fi

mac=$(arp -i eth0 -a 192.168.0.1 |grep -oE " [0-9a-f:]+ " |tr -d ' ')
echo "mac address: $mac"

model=$(curl_admin http://192.168.0.1/ | grep -oE "WD?R[0-9]+N?")
echo "found model: $model"

hwver_page="http://192.168.0.1/userRpm/SoftwareUpgradeRpm.htm"
hwver=$(curl_admin -e http://192.168.0.1/userRpm/MenuRpm.htm $hwver_page | grep -oE "$model v[0-9]+")
echo "hw version:  $hwver"

uploadurl="http://192.168.0.1/incoming/Firmware.htm"
image=""
if [ "$hwver" = "WR841N v9" ]; then
	image="openwrt-ar71xx-generic-tl-wr841n-v9-squashfs-factory.bin"
elif [ "$hwver" = "WR841N v8" ]; then
	image="openwrt-ar71xx-generic-tl-wr841n-v8-squashfs-factory.bin"
elif [ "$hwver" = "WDR3500 v1" ]; then
	image="openwrt-ar71xx-generic-tl-wdr3500-v1-squashfs-factory.bin"
elif [ "$hwver" = "WDR3600 v1" ]; then
	image="openwrt-ar71xx-generic-tl-wdr3600-v1-squashfs-factory.bin"
elif [ "$hwver" = "WDR4300 v1" ]; then
	image="openwrt-ar71xx-generic-tl-wdr4300-v1-squashfs-factory.bin"
else
	echo "UNKNOWN MODEL ($hwver), SORRY :("
	quit 2
fi

image=$(find downloads.openwrt.org -name $image)

if [ ! -e $image ]; then
	echo "Image not found: $image"
	quit 3
fi

echo -en "flashing image: $image ... "
curl_admin -e $hwver_page -F Filename=@$image $uploadurl > /dev/null
curl_admin -e $uploadurl http://192.168.0.1/userRpm/FirmwareUpdateTemp.htm > /dev/null
echo "done :)"

echo -en "waiting for router to come up again "
while ! ping -n -c 1 -W 2 192.168.1.1 > /dev/null; do
	echo -en "."
	sleep 1
done
echo " \o/"

# upload authorized keys if present
if [ -e authorized_keys ]; then
  echo -en "uploading authorized_keys ... "
  keys=`cat authorized_keys`

  ./upload_keys 192.168.1.1 "$keys" > /dev/null

  if [ $? -eq 0 ]; then
    echo "OK"
  else
    echo "failed"
    quit 4
  fi

  echo -en "stopping telnet ... "
  while ! ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@192.168.1.1 /etc/init.d/telnet stop; do
    sleep 1
  done
fi

echo
