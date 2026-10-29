
import network
import time
from machine import Pin, ADC
from umqttsimple import MQTTClient

# --- 1. CLOUD CONFIGURATION ---
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
AIO_SERVER = "io.adafruit.com"
AIO_USER = ""  # <--- CHANGE THIS!
AIO_KEY = ""             # <--- CHANGE THIS!
AIO_FEED = AIO_USER + "/feeds/factory-alarm"

# --- 2. HARDWARE SETUP ---
# Alarm LED on Pin 2
alarm_led = Pin(2, Pin.OUT)
alarm_led.value(0)

# Potentiometer on Analog Pin 34 (Simulating pipe pressure/vibration)
sensor = ADC(Pin(34))
#sensor.atten(ADC.ATTN_11V) # Allow reading full 3.3V range (0 to 4095)

# --- 3. WI-FI & MQTT CONNECTION ---
print("Connecting to Wi-Fi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected(): time.sleep(0.5)

print("Connecting to Adafruit IO...")
mqtt = MQTTClient("esp32_factory", AIO_SERVER, port=1883, user=AIO_USER, password=AIO_KEY)
mqtt.connect()
print("Cloud Ready!")
mqtt.publish(AIO_FEED, "0") # Reset dashboard alarm

# --- 4. PHASE 1: STATISTICAL CALIBRATION ("LEARNING") ---
print("\n⚙️ PHASE 1: CALIBRATING... DO NOT TOUCH THE MACHINE!")
total_value = 0
samples = 50

# Read the sensor 50 times over 5 seconds to learn what "Normal" is
for i in range(samples):
    reading = sensor.read()
    total_value += reading
    time.sleep(0.1)

baseline = total_value / samples
# Set the anomaly limit to 800 points above the normal baseline
threshold = baseline + 800 

print("✅ Calibration Complete!")
print("Normal Baseline is: {:.0f}".format(baseline))
print("Alarm will trigger if it goes above: {:.0f}".format(threshold))

# --- 5. PHASE 2: MONITORING FOR ANOMALIES ---
print("\n🏭 PHASE 2: MONITORING MACHINE HEALTH...")
alarm_active = False

while True:
    current_pressure = sensor.read()
    
    # Check for anomaly (Spike in pressure)
    if current_pressure > threshold:
        if not alarm_active:
            print("🚨 ANOMALY DETECTED! Pressure spiked to:", current_pressure)
            alarm_led.value(1)           
            
            try:
                # Send "1" for Alarm "ON" 
                mqtt.publish(AIO_FEED, "1") 
            except Exception as e:
                print("MQTT Cloud Error:", e)
                
            alarm_active = True
            time.sleep(3) # Strict 3-second cooldown for Adafruit IO
            
    else:
        if alarm_active:
            print("✅ Machine returned to normal.")
            alarm_led.value(0)
            
            try:
                # Send "0" for Alarm "OFF" 
                mqtt.publish(AIO_FEED, "0") 
            except Exception as e:
                print("MQTT Cloud Error:", e)
                
            alarm_active = False
            time.sleep(3) # Strict 3-second cooldown for Adafruit IO
            
    time.sleep(0.2)