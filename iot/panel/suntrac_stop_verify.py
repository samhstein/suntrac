import time, os

print('stopping verify....')
os.system('sudo killall suntrac_verify.py')
time.sleep(3)

print('stopping ppp.')
os.system('sudo killall pppd')
time.sleep(3)

print('stopping suntracd...')
os.system('sudo systemctl stop suntracd.service')
time.sleep(3)

print('verify stopped, done...')
