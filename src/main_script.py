# Import necessary libraries
from mcpadc import MCP  # Import the MCP class from the provided module
import Adafruit_DHT  # Import the Adafruit_DHT library to work with the DHT11 sensor
import time  # Import the time module for time-related functions
import RPi.GPIO as GPIO  # Import the RPi.GPIO module for GPIO operations
import requests  # Import the requests module for HTTP requests

# Replace with your ThingSpeak API Key and Channel ID
api_key = "DNCTR3RHNE4CUYMN"
channel_id = "2388748"

# ThingSpeak API URL
url = f"https://api.thingspeak.com/update?api_key={api_key}"

# Initialize MCP object for MCP3008 ADC (10-bit resolution, 8 channels)
# Connect ADC to GPIO pin 12
adc_module = MCP(model="3008", v_ref=5.0)

# Set the sensor type (DHT11) and the GPIO pin number to which the sensor is connected
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Define GPIO pins for actuators and push button
FAN_PIN = 17  # GPIO pin for DC fan
EXHAUST_FAN_PIN = 16  # GPIO pin for exhaust fan
LIGHT_BULB_PIN = 27  # GPIO pin for light bulb
FOGGER_PIN = 24  # GPIO pin for fogger
PUSH_BUTTON_PIN = 18  # GPIO pin for push button

# Define threshold values for sensors
TEMP_THRESHOLD = 25.0  # Temperature threshold for turning on DC fan
GAS_THRESHOLD = 500  # Gas threshold for turning on exhaust fan
LIGHT_THRESHOLD = 200  # Light intensity threshold for turning on light bulb

# Setup GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(EXHAUST_FAN_PIN, GPIO.OUT)
GPIO.setup(LIGHT_BULB_PIN, GPIO.OUT)
GPIO.setup(FOGGER_PIN, GPIO.OUT)
GPIO.setup(PUSH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize state variables for push button
current_state = False
previous_state = False

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

# Function to control actuators based on sensor values and handle button press
def control_actuators(temp, humidity, ldr_value, gas1_value, gas2_value):
    global previous_state, current_state

    # Control DC fan based on temperature
    if temp is not None:
        if temp > TEMP_THRESHOLD:
            print("Temperature is high")
            GPIO.output(FAN_PIN, GPIO.HIGH)  # Turn on DC fan
        else:
            GPIO.output(FAN_PIN, GPIO.LOW)  # Turn off DC fan

    # Control exhaust fan based on gas sensors
    elif gas1_value > GAS_THRESHOLD or gas2_value > GAS_THRESHOLD:
        print("Gas level is high")
        GPIO.output(EXHAUST_FAN_PIN, GPIO.HIGH)  # Turn on exhaust fan
    else:
        GPIO.output(EXHAUST_FAN_PIN, GPIO.LOW)  # Turn off exhaust fan

    # Control light bulb based on light intensity
    if ldr_value < LIGHT_THRESHOLD:
        print("Light intensity is low")
        GPIO.output(LIGHT_BULB_PIN, GPIO.HIGH)  # Turn on light bulb
    else:
        GPIO.output(LIGHT_BULB_PIN, GPIO.LOW)  # Turn off light bulb

    # Read the current state of the button
    current_state = GPIO.input(PUSH_BUTTON_PIN)

    # Check if the button state has changed
    if current_state != previous_state:
        # If the button is pressed, turn on fogger
        if current_state == GPIO.LOW:
            print("Pushbutton is pressed")
            GPIO.output(FOGGER_PIN, not GPIO.input(FOGGER_PIN))

        # Update the previous state
        previous_state = current_state

# Main loop for monitoring and controlling
try:
    while True:
        # Read sensor values
        temp, humidity, ldr_value, gas1_value, gas2_value = read_sensor_values()

        # Prepare data to send to ThingSpeak
        payload = {'field1': temp, 'field2': humidity, 'field3': gas1_value, 'field4': gas2_value}

        # Make the HTTP request to update ThingSpeak channel
        response = requests.post(url, params=payload)

        print(f"Temp: {temp}, Humidity: {humidity}, LDR: {ldr_value}, Gas Sensor 1: {gas1_value}, Gas Sensor 2: {gas2_value}, Response: {response.text}")

        # Control actuators
        control_actuators(temp, humidity, ldr_value, gas1_value, gas2_value)

except KeyboardInterrupt:
    print("Script terminated by user.")

finally:
    # Cleanup GPIO settings
    GPIO.cleanup()