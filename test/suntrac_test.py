import smbus
import RPi.GPIO as GPIO
import megaiosun as m
import time
import serial

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def waitPush():
  while(GPIO.input(27) == 1):
    time.sleep(0.1)
  while(GPIO.input(27) == 0):
    time.sleep(0.1)

def waitRelease():
  while(GPIO.input(27) == 0):
    time.sleep(0.1)

def checkPush():
  if GPIO.input(27) == 0 :
    return 1
  return 0

def acc():
  ACC_ADDRESS = 0x1d
  MAG_ADDRESS = 0x1e
  WHO_AM_I = 0x0f
  bus = smbus.SMBus(1)
  ret = 0

  try:
    me = bus.read_byte_data( ACC_ADDRESS, WHO_AM_I)
    if me != 0x41:
      print ("Fail to read Accelerometer! read: " + str(me))
      ret+= 1
  except Exception as e:
    print("Fail to read Accelerometer! read: " + str(e))
    ret+=1
  try:
    me = bus.read_byte_data( MAG_ADDRESS, WHO_AM_I)
    if me != 0x3d:
      print ("Fail to read Magnetometer! read: " + str(me))
      ret+=1
  except Exception as e:
      print ("Fail to read Magnetometer! read: " + str(e))
  if ret == 0 :
    print("LSM303 tested OK")
  else:
    print("LSM303 test FAIL!")
  return ret

def led():
  IO_EXP_ADD = 0x20
  IO_EXP_DIR = 0x03
  IO_EXP_OUT = 0x01
  ledList = [0, 0x12, 0x24, 0x48, 0x7e, 0x10, 0x20, 0x40, 0x02, 0x04, 0x08, 0x00]
  bus = smbus.SMBus(1)
  ret = 0
  waitRelease()
  try:
    bus.write_byte_data(IO_EXP_ADD, IO_EXP_DIR, 0x00) #set output
  except Exception as e:
    print("Fail to communicate with I/O expander! " + str(e))
    ret+=1
    return ret

  print("Check all color on both LED then press the onboard push-button")
  loop = True
  while loop:
    for i in ledList:
      time.sleep(0.5)
      bus.write_byte_data(IO_EXP_ADD, IO_EXP_OUT, ~i) #set output
      if GPIO.input(27) == 0:
        loop = False
        break

  bus.write_byte_data(IO_EXP_ADD, IO_EXP_OUT, 0xff)
  return ret

def gsm():
  ret = 0;
  try:
    ser = serial.Serial(
               port='/dev/ttyS0',
               baudrate = 115200,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=.5
           )
    #ser = serial.Serial('/dev/ttyAMA0', 115200)
  except Exception as e:
    print("Fail to open serial port! " + str(e))
    return 1
  cmd = "AT\r\n"
  try:
    ser.flushInput()
    ser.flushOutput()
    ser.write(cmd.encode('ascii'))
    lineCount = 0
    gret = ser.readline().decode('ascii')
    lineCount = 1
    gret = ser.readline().decode('ascii')
  except Exception as e:
    if(lineCount == 0):
      print("Failed to read response" + str(e))
      ret = 1
  if(gret.find('OK') >= 0):
    print("GSM/GPS module SIM868 test success")
  else:
    print("GSM/GPS module SIM868 test fail! " + gret)
    ret = 1
  ser.close()
  return ret

def term():
  print(m.get_adc_volt(1))
  print(m.get_adc_volt(2))

def mot_light():
  print("Expose to light fotodiodes and check the corresponding motor then press the push button to exit")
  waitRelease()
  loop = True
  while loop:
    led1 = m.get_adc_volt(3)
    time.sleep(0.1)
    led2 = m.get_adc_volt(4)
    time.sleep(0.1)

    if led1 > led2 and led1 > 0.2:
      m.set_motor(2,0)
      time.sleep(0.1)
      m.set_motor(1,1)
      time.sleep(0.1)
    if led2 > led1 and led2 > 0.2:
      m.set_motor(1,0)
      time.sleep(0.1)
      m.set_motor(2,1)
      time.sleep(0.1)
    if led1 <= 0.2 and led2 <= 0.2:
      m.set_motor(1,0)
      time.sleep(0.1)
      m.set_motor(2,0)
      time.sleep(0.1)

    if checkPush() :
      loop = False

print("Positioning board Testing...")
acc()
led()
print("Gsm/GPS SIM868 module Testing...")
gsm()
print("Temperature sensors Testing...")
term()
print("AC motors and light sensor testing...")
mot_light()
