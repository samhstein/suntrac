import serial

class grps:

    ser = None

    def __init__(self,):
        print("in itis")        
        try:
            self.ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
        except Exception as e:
            print("can't open serial device")


    def send_command(self, command):
        with_return = str(command) + '\n'
        self.ser.write(with_return.encode('utf-8'))

    def get_status(self):
        send_command('ATZ')
        s = ser.read(size=1024)
        print(s)

        send_command('AT+CGATT=1')
        s = ser.read(size=1024)
        print(s)

        send_command('AT+SAPBR=3,1,"CONTYPE","GPRS"')
        s = ser.read(size=1024)
        print(s)

        send_command('AT+SAPBR=3,1,"APN","jtm2m"')
        s = ser.read(size=1024)
        print(s)

        send_command('AT+SAPBR=0,1')
        s = ser.read(size=1024)
        print(s)

        send_command('AT+SAPBR=1,1')
        s = ser.read(size=1024)
        print(s)

        send_command('AT+SAPBR=2,1')
        s = ser.read(size=1024)
        print('ip: ', s)

        send_command('AT+CIPGSMLOC=1,1')
        s = ser.read(size=1024)
        print('location: ', s)
        s = ser.read(size=1024)
        print('location: ', s)

        send_command('ATZ')
        s = ser.read(size=1024)
        print(s)

        return({"ip": None, "lat": None, "lng": None})
