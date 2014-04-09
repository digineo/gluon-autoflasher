#!/bin/bash

base_fw_name="gluon-ffpb-0.3.999-exp20140409-"

ping -c 1 192.168.0.1 > /dev/null
if [ $? -ne 0 ]; then
	echo "ROUTER OFFLINE? cannot ping 192.168.0.1 :("
	exit 1
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
	exit 2
fi

echo -en "flashing image: $image ... "
curl --basic -su admin:admin -e $hwver_page -F Filename=@$image $uploadurl > /dev/null
curl --basic -su admin:admin -e $uploadurl http://192.168.0.1/userRpm/FirmwareUpdateTemp.htm > /dev/null
echo "done :)"

echo -en "waiting for router to come up again "

while ! ping -n -c 1 -W 1 192.168.1.1 > /dev/null; do
	echo -en "."
done

echo " \o/"
