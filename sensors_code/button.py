import RPi.GPIO as GPIO
import time

# Set the GPIO mode and pin numbers
button_pin = 17  # GPIO pin for the button
led_pin = 18     # GPIO pin for the LED

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_pin, GPIO.OUT)

# Initialize state variables
current_state = False
previous_state = False

try:
    while True:
        # Read the current state of the button
        current_state = GPIO.input(button_pin)

        # Check if the button state has changed
        if current_state != previous_state:
            # If the button is pressed, toggle the LED
            if current_state == GPIO.LOW:
                GPIO.output(led_pin, not GPIO.input(led_pin))
                print("LED toggled")

            # Update the previous state
            previous_state = current_state

        # Add a small delay to debounce the button
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    # Cleanup GPIO on program exit
    GPIO.cleanup()