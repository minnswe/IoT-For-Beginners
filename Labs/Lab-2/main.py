from machine import Pin
import dht
import time

# 1. Set up the LED (Actuator) on Pin 2
fan_led = Pin(2, Pin.OUT)

# 2. Set up the DHT22 Sensor on Pin 15
sensor = dht.DHT22(Pin(15))

print("Smart Farm Started!")
print("Warming up sensor for 2 seconds...")
time.sleep(2)  # CRUCIAL: The DHT22 needs 2 seconds to turn on!

while True:
    try:
        # Tell the sensor to take a measurement
        sensor.measure()
        
        # Read temperature and humidity
        temp = sensor.temperature()
        hum = sensor.humidity()
        
        # Safe way to print variables in MicroPython
        print("Temperature: {}°C | Humidity: {}%".format(temp, hum))
        
        # Edge Logic: If temp is hotter than 30, turn on the fan!
        if temp > 30.0:
            fan_led.value(1) # Turn Fan ON
            print("Warning: Too hot! Fan is ON.")
        else:
            fan_led.value(0) # Turn Fan OFF
            print("Temperature is OK. Fan is OFF.")
            
    except OSError as e:
        print("Failed to read sensor. Check if the data wire is on Pin 15!")
        
    # The DHT22 is a slow sensor. It can only be read once every 2 seconds.
    time.sleep(2)
