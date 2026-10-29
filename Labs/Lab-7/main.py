from machine import Pin, time_pulse_us
import dht
import time

# --- 1. HARDWARE SETUP ---
# DHT22 Setup (Pin 15)
temp_sensor = dht.DHT22(Pin(15))

# HC-SR04 Ultrasonic Setup
# TRIG sends the sound wave (Output). ECHO listens for the bounce (Input).
trig_pin = Pin(12, Pin.OUT)
echo_pin = Pin(14, Pin.IN)

# --- 2. ULTRASONIC FUNCTION ---
def get_distance_cm():
    # Ensure trigger is low initially
    trig_pin.value(0)
    time.sleep_us(2)
    
    # Send a 10-microsecond sound pulse
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)
    
    # Measure how long the Echo pin stays HIGH (time for sound to return)
    # Timeout is 30,000 microseconds (about 5 meters max distance)
    pulse_time = time_pulse_us(echo_pin, 1, 30000)
    
    if pulse_time < 0:
        return -1 # Error or out of range
        
    # Math: Distance = (Time * Speed of Sound) / 2
    # Speed of sound is 0.0343 cm per microsecond
    distance = (pulse_time * 0.0343) / 2
    return distance

# --- 3. MAIN LOOP & EDGE COMPUTING ---
print("System Starting... Warming up sensors.")
time.sleep(2)

while True:
    print("--- New Reading Cycle ---")
    
    # A. Read DHT22
    try:
        temp_sensor.measure()
        temp = temp_sensor.temperature()
        print("🌡️ Temp: {:.1f}°C".format(temp))
    except OSError:
        print("Failed to read DHT22")

    # B. Edge Computing: Calculate Average Distance
    # Instead of sending jumpy sensor data, we take 5 rapid readings 
    # and calculate the average locally. This saves Cloud bandwidth!
    total_distance = 0
    valid_readings = 0
    
    for i in range(5):
        dist = get_distance_cm()
        if dist > 0:
            total_distance += dist
            valid_readings += 1
        time.sleep(0.5) # Small delay between pings
        
    if valid_readings > 0:
        avg_distance = total_distance / valid_readings
        print("📏 Avg Distance: {:.1f} cm".format(avg_distance))
    else:
        print("📏 Distance: Out of Range")
        
    # In a real project, you would now MQTT Publish these variables to Adafruit IO!
    print("-------------------------")
    time.sleep(3) # Wait 3 seconds before next cycle