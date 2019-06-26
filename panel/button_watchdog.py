import RPi.GPIO as GPIO

def callback_function_print(input_pint):
  print("Input on pin", input_pin)

GPIO.setmode(GPIO.BCM)
GPIO.add_event_detect(27, GPIO.BOTH, callback=callback_function_print)
