import network
import time
import urequests 
import json
from machine import Pin

# --- CONFIGURATION ---
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
# Paste your long LINE Messaging API Token inside the quotes below!
LINE_TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN_HERE" 

# Set up the Button on Pin 13.
panic_button = Pin(13, Pin.IN, Pin.PULL_UP)

# Connect to Wi-Fi
print("Connecting to Wi-Fi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    time.sleep(0.5)
print("Wi-Fi Connected!")

# Function to send LINE message via Messaging API
def send_line_alert():
    print("Attempting to send LINE message...")
    
    # The Broadcast URL sends the message to anyone who friended your bot
    url = "https://api.line.me/v2/bot/message/broadcast"
    
    # HTTP Headers (Authentication & Data Type)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + LINE_TOKEN
    }
    
    # HTTP Payload (Formatted as JSON)
    payload_data = {
        "messages": [
            {
                "type": "text",
                "text": "WARNING! The emergency panic button was pressed!"
            }
        ]
    }
    
    # Convert Python dictionary to a JSON string
    json_payload = json.dumps(payload_data)
    
    try:
        # Send the POST request
        response = urequests.post(url, headers=headers, data=json_payload)
        
        if response.status_code == 200:
            print("Success! Check your LINE app.")
        else:
            print("Failed. Status Code:", response.status_code)
            print("Error Details:", response.text)
            
        response.close() # Always close the connection
        
    except Exception as e:
        print("Network error:", e)

# Main Loop
print("System Ready. Press the Red Button to send an alert.")
while True:
    # If button value goes to 0 (pressed)
    if panic_button.value() == 0:
        print("Button Pressed!")
        send_line_alert()
        
        # Wait 5 seconds so we don't spam the API
        time.sleep(5) 
        
    time.sleep(0.1)