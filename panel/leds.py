
#
#  control leds on the expansion board
#

import time,sys
import smbus

class leds:
    IO_EXP_ADD = 0x20
    IO_EXP_DIR = 0x03
    IO_EXP_OUT = 0x01

    ledList = [0, 0x12, 0x24, 0x48, 0x7e, 0x10, 0x20, 0x40, 0x02, 0x04, 0x08, 0x00]
    bus = smbus.SMBus(1)

    # Set up the lights
    def __init__(self,):
        try:
            self.bus.write_byte_data(IO_EXP_ADD, IO_EXP_OUT, 0x00)
        except Exception as e:
            print("Failed to communicate with I/O expander! " + str(e))

    def light_on(self, data):
        self.bus.write_byte_data(IO_EXP_ADD, IO_EXP_OUT, ledList[data])

    def lights_off(self):
        self.bus.write_byte_data(IO_EXP_ADD, IO_EXP_OUT, 0xff) 
