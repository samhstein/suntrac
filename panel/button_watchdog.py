import RPi.GPIO as GPIO
import time, leds
from datetime import datetime

pushed = False
last_time = datetime.now()
# get the lights
leds = leds.leds()

def button_push(input_pin):
    global pushed
    global last_time
    pushed = not pushed
    print("button pushed on pin", input_pin, pushed)


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push, bouncetime=500)

while True:
    time.sleep(100)
