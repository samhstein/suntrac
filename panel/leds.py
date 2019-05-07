
#
#  control leds on the expansion board
#
#

import time, sys, threading
import smbus

class leds:
    IO_EXP_ADD = 0x20
    IO_EXP_DIR = 0x03
    IO_EXP_OUT = 0x01

    LED_OFF_OFF  = 0xff
    LED_MASK = 0x00

    # port
    LED_RED_OFF = 0x02
    LED_GREEN_OFF = 0x04
    LED_BLUE_OFF = 0x08
    LED_WHITE_OFF = 0x0e
    # starboard
    LED_OFF_RED  = 0x10
    LED_OFF_GREEN  = 0x20
    LED_OFF_BLUE  = 0x40
    LED_OFF_WHITE  = 0x70

    bus = smbus.SMBus(1)
    port = 0x00
    starboard = 0x00
    blinking = False

    # Set up the lights
    def __init__(self,):
        try:
            self.write_data(0xff)
        except Exception as e:
            print("Failed to communicate with I/O expander! " + str(e))

    def write_data(self, data):
        print('wd: ', data)
        self.bus.write_byte_data(self.IO_EXP_ADD, self.IO_EXP_OUT, ~data)

    def lights_on(self, port, starboard):
        self.port = port
        self.starboard = starboard
        self.both = port | starboard
        print('lo: ', self.both)
        self.write_data(self.both)

    def lights_off(self):
        self.write_data(self.LED_OFF_OFF)

    def blink_function(self, light, freq):
        print('bb: ', self.both)
        flash = self.LED_MASK
        if light == 'port':
            flash = self.LED_MASK | self.starboard
        else:
            flash = self.port | self.LED_MASK
        while self.blinking:
            self.write_data(flash)
            time.sleep(0.1)
            self.write_data(self.both)
            time.sleep(freq)


        self.write_data(self.both)


    def blink(self, light, freq):
        self.blinking = True
        t = threading.Thread(target=self.blink_function, args=(light, freq))
        t.start()

    def stop_blinking(self):
        self.blinking = False
