#!/bin/bash

flashscript=`dirname $0`
flashscript="${flashscript}/autoflash.sh"

if [ ! -x $flashscript ]; then
	echo "Error, failed to find autoflash support script at '$flashscript'"
	exit 1
fi

while /bin/true; do

	echo -en "Waiting for virgin router to appear on 192.168.0.1 ..."
	while ! ping -n -c 1 -W 1 192.168.0.1 &> /dev/null; do
		echo -en "."
		sleep 1
	done
	echo " found"

	$flashscript
	echo "-----------------------------------------------------------------------"
	echo
done
