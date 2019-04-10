#!/usr/bin/python3

import smbus
i2c = smbus.SMBus(1)

for i in range(0x20,0x28):
  try:
     print("OK :", format(i, '02x'), i2c.read_byte_data(i,0x00))
  except:
     print("BAD:", format(i, '02x'))
