#Name: John Wish
#Student ID: 00000000
#Major: B.Tech ICT (3rd Year)
#BIC, Krirk University


#Import necessary libraries and package
from machine import Pin  
import time

# Setup Pin 2 as an Output (to send electricity out)
led = Pin(2, Pin.OUT)

print("Starting the blink program...")

# This is an infinite loop that runs forever
while True:
    led.value(1)       # Turn LED ON (1 = HIGH voltage)
    print("LED is ON.")
    time.sleep(1)      # Wait 1 second
    print("Wait 1 second.")
    led.value(0)       # Turn LED OFF (0 = LOW voltage)
    print("LED is OFF.")
    time.sleep(1)      # Wait 1 second
    print("Wait 1 second.")

