#!/usr/bin/python
import spidev
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Define custom chip select
CS_ADC = 12
GPIO.setup(CS_ADC, GPIO.OUT)

# Function to read SPI data from MCP3008 chip
def ReadChannel3008(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Function to convert ADC value to voltage
def ConvertToVoltage(value, bitdepth, vref):
    return vref * (value / (2 ** bitdepth - 1))

# Define delay between readings
delay = 0.5

while True:
    GPIO.output(CS_ADC, GPIO.LOW)
    value = ReadChannel3008(0)  # Assuming the potentiometer is connected to channel 0
    print(f"Value: {value}")
    GPIO.output(CS_ADC, GPIO.HIGH)
    voltage = ConvertToVoltage(value, 10, 3.3)  # MCP3008 is 10-bit

    print(f"Voltage: {voltage:.3f}V")


    time.sleep(delay)
