import RPi.GPIO as GPIO
import time
from datetime import datetime

pushed = False
down_time = None
push_count = 0
# get the lights
leds = leds.leds()

def button_push(input_pin):
    global pushed
    global down_time
    global push_count

    pushed = not pushed
    if pushed:
        down_time = time.time()
        push_count += 1

    if not pushed and down_time - time.time() > 5:
        print('long push')
        leds.lights_off()


    print("button pushed on pin", input_pin, pushed)


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push, bouncetime=50)

while True:
    time.sleep(100)
