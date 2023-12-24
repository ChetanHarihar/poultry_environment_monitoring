import requests
import time
import random

# ThingSpeak API Key and Channel ID
api_key = "DNCTR3RHNE4CUYMN"
channel_id = "2388748"

# ThingSpeak API URL
url = f"https://api.thingspeak.com/update?api_key={api_key}"

# Function to generate random temperature values
def generate_random_temp():
    return round(random.uniform(20.0, 30.0), 2)

# Main loop to send data to ThingSpeak
try:
    while True:
        # Generate random temperature value
        temp_value = generate_random_temp()

        # Prepare data to send to ThingSpeak
        payload = {'field1': temp_value}

        # Make the HTTP request to update ThingSpeak channel
        response = requests.post(url, params=payload)

        # Print the response from ThingSpeak
        print(f"Temperature value {temp_value} sent. Response: {response.text}")

        # Wait for 15 seconds before sending the next update
        time.sleep(15)

except KeyboardInterrupt:
    print("Script terminated by user.")