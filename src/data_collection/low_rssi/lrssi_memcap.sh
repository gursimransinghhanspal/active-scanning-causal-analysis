#!/bin/sh

# @author: Gursimran Singh
# @rollno: 2014041
#
# Checks the output of `df -h` and if the remaining memory on HDD goes below a defined threshold,
# stops the tshark process

MAX_HDD_USAGE=80

hdd_usage=`df -h | grep "/$" | awk '{print $5}' | sed "s/%//"`
if [ hdd_usage >= MAX_HDD_USAGE ] then
	sudo killall tshark;
fi