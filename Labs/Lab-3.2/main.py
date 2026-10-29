import network
import time
from machine import Pin
from umqttsimple import MQTTClient

# --- 1. CONFIGURATION ---
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
AIO_SERVER = "io.adafruit.com"
AIO_USER = "YOUR_USERNAME_HERE"     # <--- CHANGE THIS!
AIO_KEY = "YOUR_API_KEY_HERE"       # <--- CHANGE THIS!

# The MQTT Feed we want to LISTEN to
AIO_FEED = AIO_USER + "/feeds/led-control"

# --- 2. HARDWARE SETUP ---
# We will control the Green LED on Pin 2
pump_led = Pin(2, Pin.OUT)
pump_led.value(0) # Ensure it is OFF at startup

# --- 3. THE CALLBACK FUNCTION (Crucial for Week 4) ---
# This special function ONLY runs when a message arrives from the Cloud!
def mqtt_callback(topic, msg):
    print("Received Message! Topic: {}, Message: {}".format(topic, msg))
    
    # The message comes as bytes (e.g., b'ON'). We decode it to a normal string.
    command = msg.decode('utf-8')
    
    if command == "ON":
        pump_led.value(1)
        print("Action: Turning LED ON 🟢")
    elif command == "OFF":
        pump_led.value(0)
        print("Action: Turning LED OFF ⚫")

# --- 4. WI-FI CONNECTION ---
print("Connecting to Wi-Fi...", end="")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

while not wlan.isconnected():
    time.sleep(0.5)
    print(".", end="")
print(" Connected!")

# --- 5. MQTT CONNECTION & SUBSCRIPTION ---
print("Connecting to Adafruit IO...")
client = MQTTClient("esp32_listener", AIO_SERVER, port=1883, user=AIO_USER, password=AIO_KEY)

# Tell the client to use our callback function when a message arrives
client.set_callback(mqtt_callback)

try:
    client.connect()
    # Subscribe to the specific feed!
    client.subscribe(AIO_FEED)
    print("MQTT Connected & Subscribed to:", AIO_FEED)
    print("Waiting for cloud commands...")
except Exception as e:
    print("MQTT Connection Failed! Check Username and Key.")

# --- 6. MAIN LOOP ---
while True:
    try:
        # check_msg() briefly checks if Adafruit IO sent us a message.
        # If yes, it automatically triggers the mqtt_callback() function!
        client.check_msg()
    except Exception as e:
        print("Error checking message.")
        
    # A short delay prevents Wokwi from freezing
    time.sleep(0.2)