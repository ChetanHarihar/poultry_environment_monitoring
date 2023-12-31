# Import necessary libraries
from mcpadc import MCP
import Adafruit_DHT
import requests
import time
import RPi.GPIO as GPIO

# Initialize MCP object for MCP3008 ADC (10-bit resolution, 8 channels)
# Connect ADC to GPIO pin 12
adc_module = MCP(model="3008", v_ref=5.0)

# Replace with your ThingSpeak API Key and Channel ID
api_key = "YOUR_API_KEY"
channel_id = "YOUR_CHANNEL_ID"

# ThingSpeak API URL
url = f"https://api.thingspeak.com/update?api_key={api_key}"

# Set the sensor type (DHT11) and the GPIO pin number to which the sensor is connected
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Define GPIO pins for actuators and push button globally
FAN_PIN = 17  # GPIO pin for DC fan
EXHAUST_FAN_PIN = 18  # GPIO pin for exhaust fan
LIGHT_BULB_PIN = 27  # GPIO pin for light bulb
FOGGER_PIN = 22  # GPIO pin for fogger
PUSH_BUTTON_PIN = 23  # GPIO pin for push button

# Define threshold values for sensors globally
TEMP_THRESHOLD = 25.0  # Temperature threshold for turning on DC fan
GAS_THRESHOLD = 500  # Gas threshold for turning on exhaust fan
LIGHT_THRESHOLD = 200  # Light intensity threshold for turning on light bulb

# Define gas sensitivity values globally (adjust based on datasheets)
methane_sensitivity = 5.0
ammonia_sensitivity = 3.0

def convert_voltage_to_ppm(sensor_voltage, gas_type):
    """
    Converts the voltage reading from a gas sensor to parts per million (ppm) based on the gas type.

    Parameters:
    - sensor_voltage: The voltage reading from the gas sensor.
    - gas_type: The type of gas the sensor is detecting ("methane" or "ammonia").

    Returns:
    - The estimated gas concentration in parts per million (ppm).
    """
    if gas_type == "methane":
        ppm = sensor_voltage * methane_sensitivity
    elif gas_type == "ammonia":
        ppm = sensor_voltage * ammonia_sensitivity
    else:
        raise ValueError("Invalid gas type. Supported types are 'methane' and 'ammonia'.")
    return ppm

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
    gas1_ppm = convert_voltage_to_ppm(gas_sen1_voltage, gas_type="methane")

    # Read gas sensor 2 value from channel 2
    gas_sen2_channel = 2
    GPIO.output(adc_module.CS_ADC, GPIO.LOW)
    gas_sen2_raw_value = adc_module.read_channel(gas_sen2_channel)  # Read raw ADC value from gas_sen2 channel
    GPIO.output(adc_module.CS_ADC, GPIO.HIGH)
    gas_sen2_voltage = round(adc_module.convert_to_voltage(gas_sen2_raw_value), 2)  # Convert raw value to voltage and round to 2 decimal places
    gas2_ppm = convert_voltage_to_ppm(gas_sen2_voltage, gas_type="ammonia")

    # Read humidity and temperature from the DHT11 sensor
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

    # Adjust gas concentrations based on temperature (example formula, replace with your own)
    gas1_ppm *= temperature / 25.0
    gas2_ppm *= temperature / 25.0

    return temperature, humidity, ldr_voltage, gas_sen1_voltage, gas_sen2_voltage, gas1_ppm, gas2_ppm

# Function to control actuators based on sensor values and handle button press
def control_actuators(temp, ldr_value, gas1_value, gas2_value):
    # Control DC fan based on temperature
    if temp > TEMP_THRESHOLD:
        GPIO.output(FAN_PIN, GPIO.HIGH)  # Turn on DC fan
    else:
        GPIO.output(FAN_PIN, GPIO.LOW)  # Turn off DC fan

    # Control light bulb based on light intensity
    if ldr_value < LIGHT_THRESHOLD:
        GPIO.output(LIGHT_BULB_PIN, GPIO.HIGH)  # Turn on light bulb
    else:
        GPIO.output(LIGHT_BULB_PIN, GPIO.LOW)  # Turn off light bulb

    # Control exhaust fan based on gas sensors
    if gas1_value > GAS_THRESHOLD or gas2_value > GAS_THRESHOLD:
        GPIO.output(EXHAUST_FAN_PIN, GPIO.HIGH)  # Turn on exhaust fan
    else:
        GPIO.output(EXHAUST_FAN_PIN, GPIO.LOW)  # Turn off exhaust fan

    # Control fogger based on push button state
    if GPIO.input(PUSH_BUTTON_PIN) == GPIO.LOW:
        GPIO.output(FOGGER_PIN, GPIO.HIGH)  # Turn on fogger
    else:
        GPIO.output(FOGGER_PIN, GPIO.LOW)  # Turn off fogger

# Main loop to send data to ThingSpeak and control actuators
try:
    # Setup GPIO mode and pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.setup(EXHAUST_FAN_PIN, GPIO.OUT)
    GPIO.setup(LIGHT_BULB_PIN, GPIO.OUT)
    GPIO.setup(FOGGER_PIN, GPIO.OUT)
    GPIO.setup(PUSH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        # Read sensor values
        temp, humidity, ldr_value, gas1_value, gas2_value, gas1_ppm, gas2_ppm = read_sensor_values()

        # Control actuators based on sensor values
        control_actuators(temp, ldr_value, gas1_value, gas2_value)

        # Prepare data to send to ThingSpeak
        payload = {'field1': temp, 'field2': humidity, 'field3': gas1_ppm, 'field4': gas2_ppm}

        # Make the HTTP request to update ThingSpeak channel
        response = requests.post(url, params=payload)

        # Print the response from ThingSpeak
        print(f"Data sent - Temp: {temp}, Humidity: {humidity}, LDR: {ldr_value}, Gas Sensor 1: Voltage: {gas1_value} | PPM: {gas1_ppm}, Gas Sensor 2: {gas2_value} | PPM: {gas2_ppm}, Response: {response.text}")

        # Wait for some time before the next iteration
        time.sleep(0.1)  # Adjust the sleep duration as needed

except KeyboardInterrupt:
    print("Script terminated by user.")

finally:
    # Cleanup GPIO settings
    GPIO.cleanup()