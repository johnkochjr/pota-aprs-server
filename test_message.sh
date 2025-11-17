#!/bin/bash
python3 << 'PYTHON'
import aprslib
import time

# Use AI5KP with different SSID to test
TEST_CALL = "AI5KP-1"  # Your callsign with different SSID
PASSCODE = "22496"  # Same passcode as server

print("Connecting to APRS-IS...")
AIS = aprslib.IS(TEST_CALL, passwd=PASSCODE, port=14580)
AIS.connect()

print("Sending test message to AI5KP-10...")
message = f"{TEST_CALL}>APRS,TCPIP*::AI5KP-10 :POTA"
AIS.sendall(message)
print("✓ Message sent!")

time.sleep(2)
AIS.close()
print("Done! Check your server logs now.")
PYTHON
