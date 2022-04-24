#!/bin/bash

vedirectmqtt="python3 /opt/vedirect/vedirectmqtt.py -s /dev/ttyUSB0 -o localhost -p 1883 -u emonpi -w emonpimqtt2016 -t emon/mppt/"

until $vedirectmqtt; do
    echo "vedirectmqtt crashed with exit code $?.  Respawning....." >&2
    sleep 5
done
