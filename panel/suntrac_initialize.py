import json, aws_iot, os
import megaiosun

CONFIG_FILE = '/home/pi/suntrac/panel/suntrac_config.json'

proc_id = megaiosun.get_proc_id()

with open(CONFIG_FILE, 'r') as json_data_file:
    config = json.load(json_data_file)

aws_iot = aws_iot.aws_iot(proc_id)
aws_iot.sendData('suntrac/config', config)

# update and write the config file
with open(CONFIG_FILE, 'w') as json_data_file:
    config['proc_id'] = proc_id
    json.dump(config, json_data_file, indent=4)

os.system('sudo systemctl disable nodered.service')
