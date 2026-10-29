import network
import time
import dht
from machine import Pin
from umqttsimple import MQTTClient

# --- 1. CONFIGURATION ---
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
AIO_SERVER = "io.adafruit.com"
AIO_USER = "YOUR_USERNAME_HERE"     # <--- CHANGE THIS!
AIO_KEY = "YOUR_API_KEY_HERE"       # <--- CHANGE THIS!

# The MQTT Feed format
AIO_FEED = AIO_USER + "/feeds/temperature"

# --- 2. HARDWARE SETUP ---
sensor = dht.DHT22(Pin(15))
tx_led = Pin(2, Pin.OUT)  # We will use the green LED as a "Transmission" light

# --- 3. WI-FI CONNECTION ---
print("Connecting to Wi-Fi...", end="")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

while not wlan.isconnected():
    time.sleep(0.5)
    print(".", end="")
print(" Connected!")

# --- 4. MQTT CONNECTION ---
print("Connecting to Adafruit IO...")
client = MQTTClient("esp32_farm", AIO_SERVER, port=1883, user=AIO_USER, password=AIO_KEY)
try:
    client.connect()
    print("MQTT Connected Successfully!")
except Exception as e:
    print("MQTT Connection Failed! Check your Username and Key.")

# --- 5. MAIN LOOP ---
print("Warming up DHT22 sensor for 2 seconds...")
time.sleep(2)

while True:
    try:
        # Read the sensor
        sensor.measure()
        temp = sensor.temperature()
        
        print("Publishing Temperature: {}°C".format(temp))
        
        # Publish to Cloud (Data must be sent as a string)
        client.publish(AIO_FEED, str(temp))
        
        # Blink Green LED to confirm data was sent
        tx_led.value(1)
        time.sleep(0.2)
        tx_led.value(0)
        
    except OSError as e:
        print("Failed to read sensor.")
    
    # Wait 5 seconds before sending again (Adafruit free tier limit)
    time.sleep(5)