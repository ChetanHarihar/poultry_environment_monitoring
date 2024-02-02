# Import necessary libraries
from mcpadc import MCP  # Import the MCP class from the provided module
import Adafruit_DHT  # Import the Adafruit_DHT library to work with the DHT11 sensor
import time  # Import the time module for time-related functions
import RPi.GPIO as GPIO  # Import the RPi.GPIO module for GPIO operations

# Replace with your ThingSpeak API Key and Channel ID
api_key = "YOUR_API_KEY"
channel_id = "YOUR_CHANNEL_ID"

# ThingSpeak API URL
url = f"https://api.thingspeak.com/update?api_key={api_key}"

# Initialize MCP object for MCP3008 ADC (10-bit resolution, 8 channels)
# Connect ADC to GPIO pin 12
adc_module = MCP(model="3008", v_ref=5.0)

# Set the sensor type (DHT11) and the GPIO pin number to which the sensor is connected
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Define GPIO pins for actuators and push button
FAN_PIN = 2  # GPIO pin for DC fan
EXHAUST_FAN_PIN = 21  # GPIO pin for exhaust fan
LIGHT_BULB_PIN = 27  # GPIO pin for light bulb
FOGGER_PIN = 24  # GPIO pin for fogger

# Define threshold values for sensors
TEMP_THRESHOLD = 27.0  # Temperature threshold for turning on DC fan
GAS_THRESHOLD = 3  # Gas threshold for turning on exhaust fan
LIGHT_THRESHOLD = 2  # Light intensity threshold for turning on light bulb

# Setup GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(EXHAUST_FAN_PIN, GPIO.OUT)
GPIO.setup(LIGHT_BULB_PIN, GPIO.OUT)
GPIO.setup(FOGGER_PIN, GPIO.OUT)
GPIO.setup(PUSH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)


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

# Function to control actuators based on sensor values and handle button press
def control_actuators(temp, humidity, ldr_value, gas1_value, gas2_value):
    # Control DC fan based on temperature
    if temp is not None:
        if temp > TEMP_THRESHOLD:
            print("Temperature is high")
            GPIO.output(FAN_PIN, GPIO.HIGH)  # Turn on DC fan
            GPIO.output(FOGGER_PIN, GPIO.HIGH) # Turn on fogger
        else:
            GPIO.output(FAN_PIN, GPIO.LOW)  # Turn off DC fan
            GPIO.output(FOGGER_PIN, GPIO.LOW)  # Turn off fogger

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

# Main loop for monitoring and controlling
try:
    while True:
        # Read sensor values
        temp, humidity, ldr_value, gas1_value, gas2_value = read_sensor_values()

        # Control actuators
        control_actuators(temp, humidity, ldr_value, gas1_value, gas2_value)

        gas1_ppm = convert_voltage_to_ppm(gas1_value, "methane")
        gas2_ppm = convert_voltage_to_ppm(gas2_value, "ammonia")

        # Prepare data to send to ThingSpeak
        payload = {'field1': temp, 'field2': humidity, 'field3': gas1_value, 'field4': gas2_value}

        # Make the HTTP request to update ThingSpeak channel
        response = requests.post(url, params=payload)

        # Print the response from ThingSpeak
        print(f"Data sent - Temp: {temp}, Humidity: {humidity}, LDR: {ldr_value}, Gas Sensor 1: {gas1_ppm} ppm, Gas Sensor 2: {gas2_ppm} ppm. Response: {response.text}")

except KeyboardInterrupt:
    print("Script terminated by user.")

finally:
    # Cleanup GPIO settings
    GPIO.cleanup()