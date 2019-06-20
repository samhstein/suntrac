import serial

ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
print(ser)

ser.write(b'ATZ\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

ser.write(b'AT+CGATT=1\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

ser.write(b'AT+SAPBR=3,1,"CONTYPE","GPRS"\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

ser.write(b'AT+SAPBR=3,1,"APN","jtm2m"\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

ser.write(b'AT+SAPBR=1,1\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

ser.write(b'AT+SAPBR=2,1\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

ser.write(b'AT+CIPGSMLOC=1,1\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

ser.write(b'AT+SAPBR=0,1\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)

ser.write(b'ATZ\r\n')
s = ser.readline()
print('got: ', s)
s = ser.readline()
print('got: ', s)
