import network
import time
import urequests
import json
import gc
from machine import Pin, time_pulse_us
from umqttsimple import MQTTClient

# --- 1. CONFIGURATION ---
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

# Adafruit IO Config (Dashboard)
AIO_SERVER = "io.adafruit.com"
AIO_USER = ""
AIO_KEY = ""
AIO_FEED = AIO_USER + "/feeds/stock-status"

# LINE API Config (Alerts)
LINE_TOKEN = ""

# --- 2. HARDWARE SETUP ---
trig_pin = Pin(12, Pin.OUT)
echo_pin = Pin(14, Pin.IN)

def get_distance():
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)
    pulse_time = time_pulse_us(echo_pin, 1, 30000)
    if pulse_time < 0: return -1
    return (pulse_time * 0.0343) / 2

# --- 3. LINE NOTIFY FUNCTION ---
def send_line_alert():
    print("🚨 Sending RESTOCK Alert to Manager...")
    url = "https://api.line.me/v2/bot/message/broadcast"
    
    payload = {"messages": [{"type": "text", "text": "⚠️ ALERT: Shelf is EMPTY! Please restock."}]}
    json_payload = json.dumps(payload)
    payload_bytes = json_payload.encode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + LINE_TOKEN,
        'Content-Length': str(len(payload_bytes)),
        'Connection': 'close'
    }
    
    try:
        gc.collect() # Free memory
        res = urequests.post(url, headers=headers, data=payload_bytes)
        if res.status_code == 200: print("✅ LINE Alert Sent!")
        res.close()
    except Exception as e:
        print("LINE API Error:", e)

# --- 4. NETWORK SETUP ---
print("Connecting to Wi-Fi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected(): time.sleep(0.5)

print("Connecting to Adafruit IO...")
mqtt = MQTTClient("esp32_retail", AIO_SERVER, port=1883, user=AIO_USER, password=AIO_KEY)
mqtt.connect()
print("Cloud Ready!")

# --- 5. MAIN RETAIL LOGIC (STATE MACHINE) ---
current_state = "FULL"
empty_seconds_counter = 0

print("\n🛒 Smart Shelf Monitoring Started...")
mqtt.publish(AIO_FEED, "FULL") # Set dashboard to FULL on startup

while True:
    distance = get_distance()
    print("Distance: {:.1f} cm".format(distance))
    
    # LOGIC: If distance is > 50cm, the box is missing!
    if distance > 50:
        empty_seconds_counter += 1
        print("Warning: Shelf looks empty. Confirming... ({} sec)".format(empty_seconds_counter))
        
        # If it has been empty for 5 consecutive seconds, change state!
        if empty_seconds_counter >= 5 and current_state == "FULL":
            current_state = "EMPTY"
            print("❌ STATE CHANGED TO EMPTY!")
            
            # 1. Update Dashboard
            mqtt.publish(AIO_FEED, "EMPTY")
            # 2. Send LINE Alert
            send_line_alert()
            
    else:
        # If someone was just holding a box and put it back, reset the counter!
        if empty_seconds_counter > 0:
            print("Box detected again! Resetting alarm counter (False Positive Prevented).")
        empty_seconds_counter = 0
        
        # If the shelf is restocked, update state and dashboard
        if current_state == "EMPTY":
            current_state = "FULL"
            print("📦 STATE CHANGED TO FULL! Shelf Restocked.")
            mqtt.publish(AIO_FEED, "FULL")
            
    time.sleep(1) # Loop runs once every second