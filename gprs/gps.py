import serial

ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
print(ser)

print('sending: ', 'ATZ')
ser.write(b'ATZ\r\n')

print('reading')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

#ser.write(b'AT+CGATT=1')

#ser.write(b'AT+SAPBR=3,1,"CONTYPE","GPRS"')

#ser.write(b'AT+SAPBR=3,1,"APN","jtm2m"')

#ser.write(b'AT+SAPBR=1,1')

#ser.write(b'AT+SAPBR=2,1')

#ser.write(b'AT+CIPGSMLOC=1,1')

#ser.write(b'AT+SAPBR=0,1')
