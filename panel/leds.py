
#
#  control leds on the expansion board
#
#

import time,sys
import smbus

class leds:
    IO_EXP_ADD = 0x20
    IO_EXP_DIR = 0x03
    IO_EXP_OUT = 0x01
    LED_OFF_OFF  = 0xff

    LED_OFF_RED  = 0x10
    LED_OFF_GREEN  = 0x20
    LED_OFF_BLUE  = 0x40
    LED_OFF_WHITE  = 0x80

    LED_RED_OFF = 0x02
    LED_GREEN_OFF = 0x04
    LED_BLUE_OFF = 0x08
    LED_WHITE_OFF = 0x0e

    LED_RED_RED  = 0x12
    LED_GREEN_GREEN = 0x24
    LED_BLUE_BLUE  = 0x48
    LED_WHITE_WHITE  = 0x8e

    ledList = [0, 0x12, 0x24, 0x48, 0x8e, 0x10, 0x20, 0x40, 0x70, 0x02, 0x04, 0x08, 0x0e, 0x00]
    bus = smbus.SMBus(1)
    loop = False

    # Set up the lights
    def __init__(self,):
        try:
            self.write_data(0x00)
        except Exception as e:
            print("Failed to communicate with I/O expander! " + str(e))

    def write_data(self, data):
        self.bus.write_byte_data(self.IO_EXP_ADD, self.IO_EXP_OUT, data)

    def light_on(self, data):
        self.write_data(self.ledList[data])

    def lights_off(self):
        self.write_data(0xff)

    def test(self):
        self.loop = True
        while self.loop:
            print('top...')
            for l in self.ledList:
                time.sleep(1)
                print(l)
                self.bus.write_byte_data(self.IO_EXP_ADD, self.IO_EXP_OUT, ~l) #set output
            time.sleep(5)
            print('bottom...')

        self.bus.write_byte_data(IO_EXP_ADD, IO_EXP_OUT, 0xff)

    def stop_test(self):
        self.loop = False
