import RPi.GPIO as GPIO
import Adafruit_DHT
import time

# Set the sensor type (DHT11) and the GPIO pin number to which the sensor is connected
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

# Infinite loop to continuously read sensor data
while True:
    # Read humidity and temperature from the DHT11 sensor
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

    # Check if the sensor readings are valid
    if humidity is not None and temperature is not None:
        # Print the temperature and humidity in a formatted string
        print("Temperature={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
    else:
        # Print an error message if there is a sensor failure
        print("Sensor failure. Check wiring.")

    # Pause for 1 seconds before the next sensor reading
    time.sleep(1)