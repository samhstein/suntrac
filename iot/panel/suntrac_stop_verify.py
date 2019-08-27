import redis
import time, leds, os, sim868, lsm303ctr
import signal, json, aws_iot, sys
import megaiosun

CONFIG_FILE = '/home/pi/suntrac/iot/panel/suntrac_config.json'

print('stopping verify....')
os.system('sudo killall suntrac_verify')
time.sleep(3)

print('stopping ppp.')
os.system('sudo killall pppd')
time.sleep(3)

print('stopping suntracd...')
os.system('sudo systemctl stop suntracd.service')
time.sleep(3)
