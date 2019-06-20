import serial

def send_command(command):
    send_command((command + '\r\n').encode('utf-8'))


ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
print(ser)

send_command('ATZ')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

send_command('AT+CGATT=1')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

send_command('AT+SAPBR=3,1,"CONTYPE","GPRS"')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

send_command('AT+SAPBR=3,1,"APN","jtm2m"')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

send_command('AT+SAPBR=1,1')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

send_command('AT+SAPBR=2,1')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

send_command('AT+CIPGSMLOC=1,1')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

send_command('AT+SAPBR=0,1')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

send_command('ATZ')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)
