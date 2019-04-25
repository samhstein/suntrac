import smbus
import RPi.GPIO as GPIO
import megaiosun as m
import time
import serial

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

THERMISTOR_TO = 25
THERMISTOR_RO = 86000
THERMISTOR_BALANCE = 100000
THERMISTOR_BETA = 5000
INPUT_VOLTS = 5.0

def get_temp_c(volts):
    ohms = THERMISTOR_BALANCE * ((INPUT_VOLTS / volts) - 1)
    steinhart = math.log(ohms / THERMISTOR_RO) / THERMISTOR_BETA
    steinhart += 1.0 / (THERMISTOR_TO + 273.15)
    steinhart = (1.0 / steinhart) - 273.15
    return steinhart

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

    if ret == 0:
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
    v1 = m.get_adc_volt(1)
    v2 = m.get_adc_volt(2)
    print('temp 1', v1, get_temp_c(v1))
    print('temp 2', v2, get_temp_c(v2))

def light():
    v3 = m.get_adc_volt(3)
    v4 = m.get_adc_volt(4)
    print('light 1 (v3)', v3)
    print('light 2 (v4)', v4)
    print('diff', v3 - v4)

def motor():
    print('turning off both motors...')
    set_motors(0) 	# turn off all motors
    sleep(.2)
    print('turning on motor 1')
    set_motors(1)	# turn motor 1 on and motor 2 off
    sleep(2)
    print('turning on motor 2')
    set_motors(2)	# turn motor 1 on and motor 2 off
    sleep(2)
    print('turning off both motors...')
    set_motors(0) 	# turn off all motors



print("Positioning board Testing...")
acc()
led()
print("Gsm/GPS SIM868 module Testing...")
gsm()
print("Temperature sensors Testing...")
term()
print("Light sensor testing...")
light()
print("Motor testing...")
motor()
