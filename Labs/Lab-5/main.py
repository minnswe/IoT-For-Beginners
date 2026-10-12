from machine import UART
import time

# Initialize UART2 on ESP32 (RX=Pin 16, TX=Pin 17)
# Standard GPS baudrate is 9600
gps_module = UART(2, baudrate=9600, rx=16, tx=17)

print("Starting GPS Tracker...")
print("Waiting for satellite data...")

while True:
    # Check if the GPS module has sent any text
    if gps_module.any():
        # Read the raw NMEA data line
        raw_data = gps_module.readline()
        
        try:
            # Convert the byte data into a normal readable string
            nmea_sentence = raw_data.decode('utf-8').strip()
            
            # We only care about sentences starting with $GPGGA (Location Data)
            if nmea_sentence.startswith("$GPGGA"):
                print("\nRaw NMEA: " + nmea_sentence)
                
                # Split the sentence by commas
                parts = nmea_sentence.split(",")
                
                # Check if we have a valid GPS fix (part 6 is the quality indicator)
                if parts[6] != "0":
                    lat = parts[2]
                    lon = parts[4]
                    print("🚚 Truck Location Found!")
                    print("Latitude: {} | Longitude: {}".format(lat, lon))
                else:
                    print("Searching for satellites...")
                    
        except Exception as e:
            pass # Ignore decoding errors
            
    time.sleep(0.1)