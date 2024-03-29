# Import necessary libraries/modules
import spidev       # SPI (Serial Peripheral Interface) library for communication with MCP3008 ADC
import time         # Time library for introducing delays
import RPi.GPIO as GPIO  # GPIO library for Raspberry Pi

# Set the GPIO mode to BCM (Broadcom SOC channel numbering)
GPIO.setmode(GPIO.BCM)

# Open SPI bus (Create an SPI object)
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus with bus=0 and device=0
spi.max_speed_hz = 1000000  # Set the SPI bus speed to 1 MHz



EXHAUST_PIN = 24  # GPIO pin for light bulb
GPIO.setup(EXHAUST_PIN, GPIO.OUT)  # Set light pin as output 
GAS_THRESHOLD = 4.0

# Define custom chip select (CS) pin for the MCP3008 ADC
CS_ADC = 12
GPIO.setup(CS_ADC, GPIO.OUT)  # Set the CS_ADC pin as an output

# Function to read SPI data from MCP3008 chip
def read_channel_3008(channel):
    """
    Reads the analog input from the specified channel of the MCP3008 ADC.

    Parameters:
    - channel: The channel number (0-7) to read from.

    Returns:
    - The 10-bit ADC value read from the specified channel.
    """
    # MCP3008 command format: [start bit, single-ended channel selection, don't care]
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    # Combine the received bytes to get the 10-bit ADC value
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Function to convert ADC value to voltage
def convert_to_voltage(value, bit_depth, v_ref):
    """
    Converts the raw ADC value to voltage.

    Parameters:
    - value: The raw ADC value to convert.
    - bit_depth: The bit depth of the ADC (e.g., 10 bits for MCP3008).
    - v_ref: The reference voltage of the ADC (3.3V / 5V).

    Returns:
    - The voltage corresponding to the given ADC value.
    """
    return v_ref * (value / (2 ** bit_depth - 1))

# Gas sensor connected to channel 1 of MCP3008 (adjust as needed)
gas_channel = 1

# Infinite loop for continuous data reading
while True:
    # Enable the MCP3008 ADC by setting the custom chip select (CS_ADC) to low
    GPIO.output(CS_ADC, GPIO.LOW)
    
    # Read the raw ADC value from the gas sensor channel
    raw_value = read_channel_3008(gas_channel)
    
    # Disable the MCP3008 ADC by setting the custom chip select (CS_ADC) to high
    GPIO.output(CS_ADC, GPIO.HIGH)

    print(f"Raw Value: {raw_value}")

    # Convert the raw ADC value to voltage using the MCP3008's 10-bit resolution and 5V reference
    voltage = convert_to_voltage(raw_value, 10, 5)
    print(f"Voltage: {voltage:.3f}V")

    if voltage > GAS_THRESHOLD:
        print("Gas level is high")
        GPIO.output(EXHAUST_PIN, GPIO.HIGH)  # Turn on light bulb
    else:
        GPIO.output(EXHAUST_PIN, GPIO.LOW)  # Turn off light bulb
    # Wait for 1 second before the next reading
    time.sleep(1)