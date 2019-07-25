import json, aws_iot, os, sys
import megaiosun

CONFIG_FILE = '/home/pi/suntrac/panel/suntrac_config.json'

panel_serial = sys.argv[1]
print('panel_serial: ', panel_serial)

proc_id = megaiosun.get_proc_id()
print('proc_id: ', proc_id)

with open(CONFIG_FILE, 'r') as json_data_file:
    config = json.load(json_data_file)

# this gets the certs
print('getting certs')
aws_iot = aws_iot.aws_iot(proc_id)
config['proc_id'] = proc_id
config['panel_serial'] = panel_serial

# update and write the config file
with open(CONFIG_FILE, 'w') as json_data_file:
    json.dump(config, json_data_file, indent=4)

print('wrote config.')

aws_iot.sendData('suntrac/config', config)
print('sent config to aws.')

print('turning of node-red load at boot.')
os.system('sudo systemctl disable nodered.service')

print('enabling suntrac watchdog')
os.system('sudo systemctl enable watchdog.service')

print('setting hotspot values')
os.system('sudo hotspot modpar self autostart no')
ssid = 'suntrac-' + str(proc_id[:6])
os.system('sudo hotspot modpar hostapd ssid ' + ssid)
