import network
import usocket
import time
from machine import Pin

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("WIFISSID", "PASSWORD")   # Type in your credentials

# Wait until the Pico is connected
while not wlan.isconnected():
    pass

print("Connected to WiFi")
print("IP Address:", wlan.ifconfig()[0])

# Configure the pin for the transmitter
tx_pin = Pin(0, Pin.OUT) # change 0 to your chosen Pin

def send_code(pulse_length, protocol, data, repetitions):
    for _ in range(repetitions):
        send_pulse(protocol.sync_high, protocol.sync_low)  # Send the sync pattern

        for bit in data:
            if bit == '0':
                send_pulse(protocol.zero_high, protocol.zero_low)  # Send a '0'
            else:
                send_pulse(protocol.one_high, protocol.one_low)  # Send a '1'

def send_pulse(high_duration, low_duration):
    tx_pin.on()  # Set the pin to HIGH
    time.sleep_us(high_duration * pulse_length)  # Wait according to the HIGH duration
    tx_pin.off()  # Set the pin to LOW
    time.sleep_us(low_duration * pulse_length)  # Wait according to the LOW duration

# Define the protocol
class Protocol:
    def __init__(self, sync_high, sync_low, zero_high, zero_low, one_high, one_low):
        self.sync_high = sync_high
        self.sync_low = sync_low
        self.zero_high = zero_high
        self.zero_low = zero_low
        self.one_high = one_high
        self.one_low = one_low

# Define the protocol 1
protocol_1 = Protocol(sync_high=1, sync_low=31, zero_high=1, zero_low=3, one_high=3, one_low=1)

# Define the trimmed codes
on_code = "011011101011110010111000"
off_code = "011011101011110010110100"
plus_code = "011011101011110010110010"
minus_code = "011011101011110010110001"

# Define the pulse length
pulse_length = 369  # Microseconds

# Create a socket object
s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)

# Bind the socket to the IP address and port
s.bind(('0.0.0.0', 80))

# Listen for incoming connections
s.listen(5)

print("Web server started on IP:", wlan.ifconfig()[0])

# Function to handle incoming requests
def handle_request(conn, addr):
    print("New connection from:", addr)
    request = conn.recv(1024)
    request = str(request)
    if "/on" in request:
        print("Triggering On code...")
        send_code(pulse_length, protocol_1, on_code, repetitions=20)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Dieselheizung</h1><p>On code sent</p></body></html>"
    elif "/off" in request:
        print("Triggering Off code...")
        send_code(pulse_length, protocol_1, off_code, repetitions=20)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Dieselheizung</h1><p>Off code sent</p></body></html>"
    elif "/plus" in request:
        print("Triggering Plus code...")
        send_code(pulse_length, protocol_1, plus_code, repetitions=20)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><p>Plus code sent</p></body></html>"
    elif "/minus" in request:
        print("Triggering Minus code...")
        send_code(pulse_length, protocol_1, minus_code, repetitions=20)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><p>Minus code sent</p></body></html>"
    else:
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
        response += "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>"
        response += "body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }"
        response += "h1 { color: #333; }"
        response += "button { background-color: #4CAF50; color: white; padding: 20px 30px; font-size: 24px; border: none; border-radius: 4px; margin: 10px; cursor: pointer; }"
        response += "button:hover { background-color: #45a049; }"
        response += ".btn-large { padding: 30px 40px; font-size: 36px; }"
        response += "</style></head><body><h1>Dieselheizung</h1>"
        response += "<button class='btn-large' onclick='sendCode(\"/on\")'>On</button>"
        response += "<button class='btn-large' onclick='sendCode(\"/off\")'>Off</button><br>"
        response += "<button onclick='sendCode(\"/plus\")'>+</button>"
        response += "<button onclick='sendCode(\"/minus\")'>-</button>"
        response += "<script>function sendCode(url) { fetch(url); }</script></body></html>"

    conn.send(response)
    conn.close()

# Main loop
while True:
    conn, addr = s.accept()
    handle_request(conn, addr)
