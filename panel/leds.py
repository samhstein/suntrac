
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

    LED_OFF_RED  = 0x10
    LED_OFF_GREEN  = 0x20
    LED_OFF_BLUE  = 0x40
    LED_OFF_WHITE  = 0x70

    LED_RED_OFF = 0x02
    LED_GREEN_OFF = 0x04
    LED_BLUE_OFF = 0x08
    LED_WHITE_OFF = 0x0e

    LED_RED_RED  = 0x12
    LED_GREEN_GREEN = 0x24
    LED_BLUE_BLUE  = 0x48
    LED_WHITE_WHITE  = 0x7e

    ledList = [
        LED_OFF_OFF,
        LED_RED_OFF, LED_GREEN_OFF, LED_BLUE_OFF, LED_WHITE_OFF,
        LED_OFF_RED, LED_OFF_GREEN, LED_OFF_BLUE, LED_OFF_WHITE,
        LED_RED_RED, LED_GREEN_GREEN, LED_BLUE_BLUE, LED_WHITE_WHITE
    ]
    bus = smbus.SMBus(1)
    port = 0x00
    startboard = 0x00
    loop = False

    # Set up the lights
    def __init__(self,):
        try:
            self.write_data(0x00)
        except Exception as e:
            print("Failed to communicate with I/O expander! " + str(e))

    def write_data(self, data):
        self.bus.write_byte_data(self.IO_EXP_ADD, self.IO_EXP_OUT, data)

    def lights_on(self, port, starboard):
        self.port = port
        self.starboard = starboard
        both = port | starboard
        self.write_data(~both)

    def lights_off(self):
        self.write_data(0xff)

    def test(self):
        self.loop = True
        while self.loop:
            for l in self.ledList:
                time.sleep(1)
                print(l)
                self.bus.write_byte_data(self.IO_EXP_ADD, self.IO_EXP_OUT, ~l) #set output

    def stop_test(self):
        self.loop = False
