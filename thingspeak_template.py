import requests
import time
import random

# Replace with your ThingSpeak API Key and Channel ID
api_key = "YOUR_API_KEY"
channel_id = "YOUR_CHANNEL_ID"

# ThingSpeak API URL
url = f"https://api.thingspeak.com/update?api_key={api_key}"

# Function to generate random sensor values
def generate_random_data():
    temp_value = round(random.uniform(20.0, 30.0), 2)
    humidity_value = round(random.uniform(40.0, 70.0), 2)
    gas1_value = round(random.uniform(980.0, 1020.0), 2)
    gas2_value = round(random.uniform(980.0, 1020.0), 2)

    return temp_value, humidity_value, gas1_value, gas2_value

# Main loop to send data to ThingSpeak
try:
    while True:
        # Generate random sensor values
        temp, humidity, gas1_value, gas2_value = generate_random_data()

        # Prepare data to send to ThingSpeak
        payload = {'field1': temp, 'field2': humidity, 'field3': gas1_value, 'field4': gas2_value}

        # Make the HTTP request to update ThingSpeak channel
        response = requests.post(url, params=payload)

        # Print the response from ThingSpeak
        print(f"Data sent - Temp: {temp}, Humidity: {humidity}, Pressure: {pressure}, Light: {light}. Response: {response.text}")

        # Wait for 15 seconds before sending the next update
        time.sleep(15)

except KeyboardInterrupt:
    print("Script terminated by user.")