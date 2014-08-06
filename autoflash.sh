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

# download missing firmware images
for model in tp-link-tl-wr841n-nd-v8 tp-link-tl-wr841n-nd-v9 tp-link-tl-wdr3500-v1 tp-link-tl-wdr3600-v1 tp-link-tl-wdr4300-v1; do
	if [ ! -r "images/${base_fw_name}${model}.bin" ]; then
		echo -en "Downloading image for '$model' ... "
		wget -q "${base_fw_url}${base_fw_name}-${model}.bin" -O "images/${base_fw_name}${model}.bin"
		if [ $? -eq 0 ]; then
			echo "OK"
		else
			echo "ERROR"
			rm "images/${base_fw_name}${model}.bin" 2>/dev/null
			echo "Failed to download firmware. Please ensure the firmware for '${base_fw_name}${model}' is present in images/ directory."
			quit 3
		fi
	fi
done

ping -n -c 1 -W 1 192.168.0.1 > /dev/null
if [ $? -ne 0 ]; then
	echo "ROUTER OFFLINE? cannot ping 192.168.0.1 :("
	quit 1
fi

model=$(curl_admin http://192.168.0.1/ | grep -oE "WD?R[0-9]+N?")
echo "found model: $model"

mac=$(arp -i eth0 -a 192.168.0.1 |grep -oE " [0-9a-f:]+ " |tr -d ' ')
echo "mac address: $mac"

hwver_page="http://192.168.0.1/userRpm/SoftwareUpgradeRpm.htm"
hwver=$(curl_admin -e http://192.168.0.1/userRpm/MenuRpm.htm $hwver_page | grep -oE "$model v[0-9]+")
echo "hw version: $hwver"

uploadurl="http://192.168.0.1/incoming/Firmware.htm"
image=""
if [ "$hwver" = "WR841N v9" ]; then
	image="${base_fw_name}tp-link-tl-wr841n-nd-v9.bin"
elif [ "$hwver" = "WR841N v8" ]; then
	image="${base_fw_name}tp-link-tl-wr841n-nd-v8.bin"
elif [ "$hwver" = "WDR3500 v1" ]; then
	image="${base_fw_name}tp-link-tl-wdr3500-v1.bin"
elif [ "$hwver" = "WDR3600 v1" ]; then
	image="${base_fw_name}tp-link-tl-wdr3600-v1.bin"
elif [ "$hwver" = "WDR4300 v1" ]; then
	image="${base_fw_name}tp-link-tl-wdr4300-v1.bin"
else
	echo "UNKNOWN MODEL ($hwver), SORRY :("
	quit 2
fi

# prepend images/ subdirectory to filename
image="images/$image"

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
echo
