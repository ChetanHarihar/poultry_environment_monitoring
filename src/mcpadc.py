# Import the spidev module for SPI communication
import spidev

# Import the RPi.GPIO module for GPIO operations
import RPi.GPIO as GPIO

# Initialize the time module for time-related functions
import time

# Define a class named MCP for interacting with MCP ADC
class MCP:
    def __init__(self, model="3008", spi_bus=0, spi_device=0, v_ref=5.0):
        # Set the GPIO mode to BCM (Broadcom SOC channel numbering)
        GPIO.setmode(GPIO.BCM)

        # Check if the provided model is supported
        if model not in ["3004", "3008"]:
            raise ValueError("Invalid MCP model. Supported models are '3004' or '3008'.")

        # Open SPI bus (Create an SPI object)
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)  # Open SPI bus with specified bus and device
        self.spi.max_speed_hz = 1000000  # Set the SPI bus speed to 1 MHz

        # Define custom chip select (CS) pin for the MCP ADC
        self.CS_ADC = 12
        GPIO.setup(self.CS_ADC, GPIO.OUT)  # Set the CS_ADC pin as an output

        # Reference voltage for ADC
        self.v_ref = v_ref

        # Determine the bit depth and max channels based on the model (MCP3004 or MCP3008)
        if model == "3008":
            self.bit_depth = 10
            self.max_channels = 7
        elif model == "3004":
            self.bit_depth = 10
            self.max_channels = 3

    def read_channel(self, channel):
        """
        Reads the analog input from the specified channel of the MCP ADC.

        Parameters:
        - channel: The channel number (0 to max_channels) to read from.

        Returns:
        - The ADC value read from the specified channel.
        """
        if not 0 <= channel <= self.max_channels:
            raise ValueError(f"Invalid channel. Please enter a channel between 0 and {self.max_channels}.")

        # MCP command format: [start bit, single-ended channel selection, don't care]
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        # Combine the received bytes to get the ADC value
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    def convert_to_voltage(self, value):
        """
        Converts the raw ADC value to voltage.

        Parameters:
        - value: The raw ADC value to convert.

        Returns:
        - The voltage corresponding to the given ADC value.
        """
        return self.v_ref * (value / (2 ** self.bit_depth - 1))

    def cleanup(self):
        """
        Clean up GPIO and SPI resources.
        """
        GPIO.cleanup()
        self.spi.close()