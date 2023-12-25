from mcpadc import MCP  # Import the MCP class from the provided module
import Adafruit_DHT  # Import the Adafruit_DHT library to work with the DHT11 sensor
import requests  # Import the requests module for HTTP requests
import time  # Import the time module for time-related functions

# Replace with your ThingSpeak API Key and Channel ID
api_key = "YOUR_API_KEY"
channel_id = "YOUR_CHANNEL_ID"

# ThingSpeak API URL
url = f"https://api.thingspeak.com/update?api_key={api_key}"

# Initialize MCP object for MCP3008 ADC (10-bit resolution, 8 channels)
adc_module = MCP(model="3008", v_ref=5.0)  # Create an MCP object with specified model and reference voltage

# Set the sensor type (DHT11) and the GPIO pin number to which the sensor is connected
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Function to read sensor values
def read_sensor_values():
    # Read LDR value from channel 0
    ldr_channel = 0
    ldr_raw_value = adc_module.read_channel(ldr_channel)  # Read raw ADC value from LDR channel
    ldr_voltage = adc_module.convert_to_voltage(ldr_raw_value)  # Convert raw value to voltage

    # Read gas sensor 1 value from channel 1
    gas_sen1_channel = 1
    gas_sen1_raw_value = adc_module.read_channel(gas_sen1_channel)  # Read raw ADC value from gas_sen1 channel
    gas_sen1_voltage = adc_module.convert_to_voltage(gas_sen1_raw_value)  # Convert raw value to voltage

    # Read gas sensor 2 value from channel 2
    gas_sen2_channel = 2
    gas_sen2_raw_value = adc_module.read_channel(gas_sen2_channel)  # Read raw ADC value from gas_sen2 channel
    gas_sen2_voltage = adc_module.convert_to_voltage(gas_sen2_raw_value)  # Convert raw value to voltage

    # Read humidity and temperature from the DHT11 sensor
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

    return temperature, humidity, gas_sen1_voltage, gas_sen2_voltage

# Main loop to send data to ThingSpeak
try:
    while True:
        # Read sensor values
        temp, humidity, gas1_value, gas2_value = read_sensor_values()

        # Prepare data to send to ThingSpeak
        payload = {'field1': temp, 'field2': humidity, 'field3': gas1_value, 'field4': gas2_value}

        # Make the HTTP request to update ThingSpeak channel
        response = requests.post(url, params=payload)

        # Print the response from ThingSpeak
        print(f"Data sent - Temp: {temp}, Humidity: {humidity}, Gas Sensor 1: {gas1_value}, Gas Sensor 2: {gas2_value}. Response: {response.text}")

        # Wait for 15 seconds before sending the next update
        time.sleep(15)

except KeyboardInterrupt:
    print("Script terminated by user.")