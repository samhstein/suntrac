import RPi.GPIO as GPIO
import time


def button_push(input_pin):
    pushed = not pushed
    print("button pushed on pin", input_pin, pushed)


pushed = False
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push)
time.sleep(100)
