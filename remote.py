import network, usocket, time
from machine import Pin

#Turn on the LED
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("SSID", "PASSWORD")            # Put in your WIFI Credentials
while not wlan.isconnected(): pass
print(f"Connected to WiFi, IP: {wlan.ifconfig()[0]}")

# Configure pin and protocol
tx_pin = Pin(16, Pin.OUT)
class Protocol:
    def __init__(self, sync, zero, one):
        self.sync_high, self.sync_low = sync
        self.zero_high, self.zero_low = zero
        self.one_high, self.one_low = one
protocol_1 = Protocol((1, 31), (1, 3), (3, 1))

# Define codes
on_code = "011011101011110010111000"
off_code = "011011101011110010110100"
plus_code = "011011101011110010110010"
minus_code = "011011101011110010110001"
pulse_length = 369

def send_code(code, repetitions=20):
    for _ in range(repetitions):
        send_pulse(protocol_1.sync_high, protocol_1.sync_low)
        for bit in code:
            if bit == '0':
                send_pulse(protocol_1.zero_high, protocol_1.zero_low)
            else:
                send_pulse(protocol_1.one_high, protocol_1.one_low)

def send_pulse(high_duration, low_duration):
    tx_pin.on()
    time.sleep_us(high_duration * pulse_length)
    tx_pin.off()
    time.sleep_us(low_duration * pulse_length)

# Start web server
s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
s.bind(('192.168.0.17', 80))
s.listen(5)

def handle_request(conn, addr):
    request = str(conn.recv(1024))
    if "/on" in request:
        print("Triggering On code...")
        send_code(on_code)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Dieselheizung</h1><p>On code sent</p></body></html>"
    elif "/off" in request:
        print("Triggering Off code...")
        send_code(off_code)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Dieselheizung</h1><p>Off code sent</p></body></html>"
    elif "/plus" in request:
        print("Triggering Plus code...")
        send_code(plus_code)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><p>Plus code sent</p></body></html>"
    elif "/minus" in request:
        print("Triggering Minus code...")
        send_code(minus_code)
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

while True:
    conn, addr = s.accept()
    handle_request(conn, addr)
