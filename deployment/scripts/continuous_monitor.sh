#!/bin/bash

echo "Continuous monitoring started..."

while true
do
    ./deployment/scripts/monitor.sh
    sleep 10
done
