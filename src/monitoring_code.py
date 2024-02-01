from mcpadc import MCP  # Import the MCP class from the provided module
import Adafruit_DHT  # Import the Adafruit_DHT library to work with the DHT11 sensor
import requests  # Import the requests module for HTTP requests
import time  # Import the time module for time-related functions
import RPi.GPIO as GPIO  # Import the RPi.GPIO module for GPIO operations

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

# Function to convert output_voltage to ppm
def convert_voltage_to_ppm(sensor_voltage, gas_type):
    """
    Converts the voltage reading from a gas sensor to parts per million (ppm) based on the gas type.

    Parameters:
    - sensor_voltage: The voltage reading from the gas sensor.
    - gas_type: The type of gas the sensor is detecting ("methane" or "ammonia").

    Returns:
    - The estimated gas concentration in parts per million (ppm).
    """
    methane_sensitivity = 5.0
    ammonia_sensitivity = 3.0

    if gas_type == "methane":
        ppm = sensor_voltage * methane_sensitivity
    elif gas_type == "ammonia":
        ppm = sensor_voltage * ammonia_sensitivity
    else:
        raise ValueError("Invalid gas type. Supported types are 'methane' and 'ammonia'.")
    return ppm

# Function to read sensor values
def read_sensor_values():
    # Read LDR value from channel 0
    ldr_channel = 0
    GPIO.output(adc_module.CS_ADC, GPIO.LOW)
    ldr_raw_value = adc_module.read_channel(ldr_channel)  # Read raw ADC value from LDR channel
    GPIO.output(adc_module.CS_ADC, GPIO.HIGH)
    ldr_voltage = round(adc_module.convert_to_voltage(ldr_raw_value), 2)  # Convert raw value to voltage and round to 2 decimal places

    # Read gas sensor 1 value from channel 1
    gas_sen1_channel = 1
    GPIO.output(adc_module.CS_ADC, GPIO.LOW)
    gas_sen1_raw_value = adc_module.read_channel(gas_sen1_channel)  # Read raw ADC value from gas_sen1 channel
    GPIO.output(adc_module.CS_ADC, GPIO.HIGH)
    gas_sen1_voltage = round(adc_module.convert_to_voltage(gas_sen1_raw_value), 2)  # Convert raw value to voltage and round to 2 decimal places

    # Read gas sensor 2 value from channel 2
    gas_sen2_channel = 2
    GPIO.output(adc_module.CS_ADC, GPIO.LOW)
    gas_sen2_raw_value = adc_module.read_channel(gas_sen2_channel)  # Read raw ADC value from gas_sen2 channel
    GPIO.output(adc_module.CS_ADC, GPIO.HIGH)
    gas_sen2_voltage = round(adc_module.convert_to_voltage(gas_sen2_raw_value), 2)  # Convert raw value to voltage and round to 2 decimal places

    # Read humidity and temperature from the DHT11 sensor
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

    return temperature, humidity, ldr_voltage, gas_sen1_voltage, gas_sen2_voltage

# Main loop to send data to ThingSpeak
try:
    while True:
        # Read sensor values
        temp, humidity, ldr_value, gas1_value, gas2_value = read_sensor_values()

        # convert gas values to ppm values
        gas1_value = convert_voltage_to_ppm(gas1_value, "methane")
        gas2_value = convert_voltage_to_ppm(gas2_value, "ammonia")

        # Prepare data to send to ThingSpeak
        payload = {'field1': temp, 'field2': humidity, 'field3': gas1_value, 'field4': gas2_value}

        # Make the HTTP request to update ThingSpeak channel
        response = requests.post(url, params=payload)

        # Print the response from ThingSpeak
        print(f"Data sent - Temp: {temp}, Humidity: {humidity}, LDR: {ldr_value}, Gas Sensor 1: {gas1_value}, Gas Sensor 2: {gas2_value}. Response: {response.text}")
        
        # Wait for 15 seconds before sending the next update
        time.sleep(15)

except KeyboardInterrupt:
    print("Script terminated by user.")