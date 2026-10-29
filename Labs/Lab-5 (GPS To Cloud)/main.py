import network
import time
from umqttsimple import MQTTClient

# --- 1. CLOUD CONFIGURATION ---
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
AIO_SERVER = "io.adafruit.com"
AIO_USER = "user_name"     # <--- CHANGE THIS!
AIO_KEY = "api_key"       # <--- CHANGE THIS!

# Notice the "/csv" at the end! This is required by Adafruit Map blocks.
AIO_LOCATION_FEED = AIO_USER + "/feeds/location/csv"

# --- 2. MOCK GPS DATA (Bangkok) ---
# Route: Lat Pla Khao BTS (PK18) to Government Complex BTS (PK12)
mock_nmea_data = [
    # 1. Lat Pla Khao (PK18) - Exact Coord: 13.8633N, 100.6138E
    "$GPGGA,120000.00,1351.76759,N,10037.06653,E,1,08,0.9,54.7,M,0.0,M,,*67", 
    
    # 2. Ram Inthra 3 (PK17) - Exact Coord: 13.8711N, 100.6030E
    "$GPGGA,120000.00,1352.24938,N,10036.17197,E,1,08,0.9,54.7,M,0.0,M,,*62", 
    
    # 3. Wat Phra Sri Mahathat (PK16) - Exact Coord: 13.8752N, 100.5966E
    "$GPGGA,080010,1352.5167,N,10035.8000,E,1,08,0.9,545.4,M,46.9,M,,*47", 
    
    # 4. Rajabhat Phranakhon (PK15) - Exact Coord: 13.8805N, 100.5913E
    "$GPGGA,120000.00,1352.78886,N,10035.37059,E,1,08,0.9,54.7,M,0.0,M,,*66", 
    
    # 5. Lak Si (PK14) - Exact Coord: 13.8825N, 100.5794E
    "$GPGGA,120000.00,1353.04695,N,10034.95483,E,1,08,0.9,54.7,M,0.0,M,,*67", 
    
    # 6. National Telecom (PK13) - Exact Coord: 13.8850N, 100.5683E
    "$GPGGA,120000.00,1353.24592,N,10034.54596,E,1,08,0.9,54.7,M,0.0,M,,*63", 
    
    # 7. Government Complex (PK12) - Exact Coord: 13.8872N, 100.5647E
    "$GPGGA,120000.00,1353.44173,N,10034.04010,E,1,08,0.9,54.7,M,0.0,M,,*6A"  
]

# --- 3. WI-FI & MQTT CONNECTION ---
print("Connecting to Wi-Fi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    time.sleep(0.5)

print("Connecting to Adafruit IO...")
client = MQTTClient("esp32_gps", AIO_SERVER, port=1883, user=AIO_USER, password=AIO_KEY)
client.connect()
print("Cloud Connected! Starting Truck Tracker...")

# --- 4. MAIN TRACKING LOOP ---
for sentence in mock_nmea_data: # We use a FOR loop so it stops when the trip is done
    
    parts = sentence.split(",")
    
    if parts[0] == "$GPGGA" and parts[6] == "1":
        # Do the GPS Math (Degrees + Minutes/60)
        lat_deg = float(parts[2][0:2])
        lat_min = float(parts[2][2:])
        final_lat = lat_deg + (lat_min / 60.0)
        
        lon_deg = float(parts[4][0:3])
        lon_min = float(parts[4][3:])
        final_lon = lon_deg + (lon_min / 60.0)
        
        print("\n Location: Lat {:.6f}, Lon {:.6f}".format(final_lat, final_lon))
        
        # Format required by Adafruit IO Map: "Value,Lat,Lon,Elevation"
        # We use "1" for value, and "0" for elevation.
        csv_payload = "1,{:.6f},{:.6f},0".format(final_lat, final_lon)
        
        print("Uploading to Map: " + csv_payload)
        client.publish(AIO_LOCATION_FEED, csv_payload)
        
    # Wait 5 seconds before sending the next point to Adafruit IO
    time.sleep(5) 

print("\n Truck has arrived at destination!")