#!/bin/bash

out=/home/pi/output.txt
rm -f $out

(
	echo "I am about to run without a screen"

	echo "Here is the wireless status"
	ifconfig
	cd /home/pi
	sudo ./jamclient_screenless.py

) >> $out
