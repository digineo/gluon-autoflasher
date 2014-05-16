#!/bin/bash

base_fw_name="gluon-ffpb-0.4~beta2-"

function quit() {
	if [ x"${BASH_SOURCE[0]}" == x"$0" ]; then
		exit $*
	else
		return $*
	fi
}

# download missing firmware images
for model in tp-link-tl-wr841n-nd-v8 tp-link-tl-wr841n-nd-v9; do
	if [ ! -r "images/${base_fw_name}${model}.bin" ]; then
		echo -en "Downloading image for '$model' ... "
		wget -q "http://firmware.paderborn.freifunk.net/stable/${base_fw_name}${model}.bin" -O "images/${base_fw_name}${model}.bin"
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

model=$(curl --basic -su admin:admin http://192.168.0.1/ | grep -oE "WR[0-9]+N")
echo "found model: $model"

hwver_page="http://192.168.0.1/userRpm/SoftwareUpgradeRpm.htm"
hwver=$(curl --basic -su admin:admin -e http://192.168.0.1/userRpm/MenuRpm.htm $hwver_page | grep -oE "$model v[0-9]+")
echo "hw version: $hwver"

uploadurl="http://192.168.0.1/incoming/Firmware.htm"
image=""
if [ "$hwver" = "WR841N v9" ]; then
	image="${base_fw_name}tp-link-tl-wr841n-nd-v9.bin"
elif [ "$hwver" = "WR841N v8" ]; then
	image="${base_fw_name}tp-link-tl-wr841n-nd-v8.bin"
else
	echo "UNKNOWN MODEL ($hwver), SORRY :("
	quit 2
fi

# prepend images/ subdirectory to filename
image="images/$image"

echo -en "flashing image: $image ... "
curl --basic -su admin:admin -e $hwver_page -F Filename=@$image $uploadurl > /dev/null
curl --basic -su admin:admin -e $uploadurl http://192.168.0.1/userRpm/FirmwareUpdateTemp.htm > /dev/null
echo "done :)"

echo -en "waiting for router to come up again "

while ! ping -n -c 1 -W 3 192.168.1.1 > /dev/null; do
	echo -en "."
done

echo " \o/"
echo
