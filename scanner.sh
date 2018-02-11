#!/bin/bash

# ====================================
# scanner.sh
# Description: Wrap wget to scan ports 
#     of a targeted IP.
# 
# Usage: ./scanner [-i] [-p]  
#
#
# Args: 
#     [-i]     : ip address to scan
#     [-p]    : port range to scan 
#
#
# Daniel Thurau
# 1402341
# dthurau@ucsc.edu
# CMPS-122 Lab2

OPTIND=1

$ip
$portrange


while getopts "i:p:" opt; do
    case "$opt" in
    i)  ip=$OPTARG
        ;;
    p)  portrange=$OPTARG
        ;;
    esac
done
shift $((OPTIND -1))


#https://stackoverflow.com/questions/35979238/how-can-i-parse-capture-strings-separated-by-dashes
IFS=- read lower upper <<<"$portrange"

echo "=============================="
echo "Port Scan:"
echo "=============================="

echo
echo "Scanning IP address: "$ip
echo "Scanning ports between "$lower" and "$upper
echo
echo "Beginning Scan..."


OPENPORTS=""




for i in `seq $lower $upper`
do 
	echo $ip:$i
	output=`wget --timeout=0.05 --tries=1 -qO- $ip:$i`
	if [ -z "$output" ]
	then
	      :
	else
	      OPENPORTS=$OPENPORTS","$i
	      # echo $OPENPORTS
	fi
done

echo 
echo
echo "-----------------"
echo "Results of Scan"
echo "-----------------"
echo $OPENPORTS




