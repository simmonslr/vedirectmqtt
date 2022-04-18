# vedirectmqtt
Victron VeDirect Protocol to MQTT

This Python script will parse the VeDirect protocol data from Victron devices and post to an MQQT broker.

The core parsing logic came from the following project: https://github.com/karioja/vedirect. Additional exception handling and data validation was added to filter invalid data items. This code also loads once and runs until stopped rather than being loaded for each transaction. Victron shunt devices (BMV) send a full set of data in two subsequent events, and loading the python code for each transaction caused data retrieval to be hit-and-miss. This code listens continously for data.

See the description.txt file for usage details.
