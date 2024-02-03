import RPi.GPIO as GPIO
import time

# Set GPIO mode to GPIO.BCM or GPIO.BOARD
GPIO.setmode(GPIO.BCM)

# Define GPIO pins
TRIG = 20  # Example GPIO 23 for Trigger
ECHO = 16  # Example GPIO 24 for Echo
BUZZER = 18  # GPIO pin for the buzzer

# Set up the GPIO channels - two outputs (TRIG and BUZZER), and one input (ECHO)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

def get_distance():
    # Ensure the trigger pin is low for a clean start
    GPIO.output(TRIG, False)
    time.sleep(0.5)  # Settle time

    # Generate a 10us pulse on the trigger pin
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    # Monitor echo pin for the duration of the echo pulse
    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    # Calculate pulse duration and distance
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2  # Speed of sound wave divided by 2 (to and from)

    return distance

def control_buzzer(distance):
    if distance > 10:
        GPIO.output(BUZZER, GPIO.HIGH)  # Turn buzzer on
    else:
        GPIO.output(BUZZER, GPIO.LOW)   # Turn buzzer off

try:
    while True:
        dist = get_distance()
        print(f"Distance: {dist:.2f} cm")
        control_buzzer(dist)
        time.sleep(1)

# Clean up the GPIO pins before ending
except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()
