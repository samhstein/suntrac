import RPi.GPIO as GPIO
import time

def callback_function_print(input_pin):
  print("Input on pin", input_pin)

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=callback_function_print)
time.sleep(100)
