# Import necessary libraries
from mcpadc import MCP
import Adafruit_DHT
import time
import RPi.GPIO as GPIO

# Initialize MCP object for MCP3008 ADC (10-bit resolution, 8 channels)
adc_module = MCP(model="3008", v_ref=5.0)

# Set the sensor type (DHT11) and the GPIO pin number to which the sensor is connected
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Define GPIO pins for actuators
FAN_PIN = 17  # GPIO pin for DC fan
EXHAUST_FAN_PIN = 18  # GPIO pin for exhaust fan
LIGHT_BULB_PIN = 27  # GPIO pin for light bulb
FOGGER_PIN = 23  # GPIO pin for fogger
PUSH_BUTTON_PIN = 22  # GPIO pin for push button

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

# Function to control actuators based on sensor values
def control_actuators(temp, gas1_value, gas2_value, ldr_value):
    global previous_state, current_state
    # Control DC fan based on temperature
    if temp is not None:
        if temp > TEMP_THRESHOLD:
            GPIO.output(FAN_PIN, GPIO.HIGH)  # Turn on DC fan
        else:
            GPIO.output(FAN_PIN, GPIO.LOW)  # Turn off DC fan

    # Control exhaust fan based on gas sensors
    if gas1_value > GAS_THRESHOLD or gas2_value > GAS_THRESHOLD:
        GPIO.output(EXHAUST_FAN_PIN, GPIO.HIGH)  # Turn on exhaust fan
    else:
        GPIO.output(EXHAUST_FAN_PIN, GPIO.LOW)  # Turn off exhaust fan

    # Control light bulb based on light intensity
    if ldr_value < LIGHT_THRESHOLD:
        GPIO.output(LIGHT_BULB_PIN, GPIO.HIGH)  # Turn on light bulb
    else:
        GPIO.output(LIGHT_BULB_PIN, GPIO.LOW)  # Turn off light bulb

    # Read the current state of the button
        current_state = GPIO.input(PUSH_BUTTON_PIN)

        # Check if the button state has changed
        if current_state != previous_state:
            # If the button is pressed, turn on fogger
            if current_state == GPIO.LOW:
                GPIO.output(FOGGER_PIN, not GPIO.input(FOGGER_PIN))

            # Update the previous state
            previous_state = current_state

# Main loop for monitoring and controlling
try:
    while True:
        # Read sensor values
        temp, humidity, ldr_value, gas1_value, gas2_value = read_sensor_values()

        # Control actuators based on sensor values
        control_actuators(temp, gas1_value, gas2_value, ldr_value)

        # Print sensor values (you can replace this with logging or other forms of output)
        print(f"Temp: {temp}, Humidity: {humidity}, LDR: {ldr_value}, Gas Sensor 1: {gas1_value}, Gas Sensor 2: {gas2_value}")

        # Add a delay to avoid excessive readings
        time.sleep(5)

except KeyboardInterrupt:
    print("Script terminated by user.")

finally:
    # Cleanup GPIO settings
    GPIO.cleanup()