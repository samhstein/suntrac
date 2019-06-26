import RPi.GPIO as GPIO
import time

def button_rise(input_pin):
  print("rise on pin", input_pin)

 def button_fall(input_pin):
   print("fall on pin", input_pin)

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.RISING, callback=button_rise)
GPIO.add_event_detect(27, GPIO.FALLING, callback=button_fall)
time.sleep(100)
