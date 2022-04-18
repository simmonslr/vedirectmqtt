# vedirectmqtt
Victron VeDirect Protocol to MQTT

This Python script will parse the VeDirect protocol data from Victron devices and post to an MQQT broker.

The core parsing logic came from the following project: https://github.com/karioja/vedirect. Additional exception handling and data validation was added to filter out invalid data items.

This code may be used to post Victron data to an emonpi using the following parameters:

  serPort:  /dev/ttyUSB1
  mqHost:   localhost
  mqPort:   1883
  mqUID:    emonpi
  mqPW:     emonpimqtt2016
  mqTopic:  emon/mppt
