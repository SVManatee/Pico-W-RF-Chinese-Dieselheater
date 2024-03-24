I have uploaded a code for a Pi Pico W to transmit codes via RF Transmitter to control a chinese diesel heater via Webpage. 
Connect a cheap RFTransmitter to the Pico W (VCC to 3V3, DATA to Pin 16, GND to GND), upload the code and rename it main.py and restart the Pico. 
(Put your WIFI Creds in first ;))

Now after restarting, browse the Webpage of the Pico (You can see the IP in Thonny Terminal if its not known)
You will see On/Off,+/-.
Add the Remotecontrol to your dieselheater LCD: Push Powerbutton and Arrow down until OC shows up. Then press on Button on the Page.
The LCD should fall back in normal Mode once it succeeded.

Start diesel-heater from Bed ;)
