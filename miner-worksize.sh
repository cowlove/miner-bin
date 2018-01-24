#!/bin/bash
# 
# Old tool to change the worksize: param in amd.txt configuration file

echo $1
sed -i "s/\"worksize\" : [0-9]/\"worksize\" : $1/' xmr-stak/amd.txt

