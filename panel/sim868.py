import serial

class sim868:

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
        self.send_command('ATZ')
        s = self.ser.read(size=1024)

        self.send_command('AT+CGATT=1')
        s = self.ser.read(size=1024)

        self.send_command('AT+SAPBR=3,1,"CONTYPE","GPRS"')
        s = self.ser.read(size=1024)

        self.send_command('AT+SAPBR=3,1,"APN","jtm2m"')
        s = self.ser.read(size=1024)

        self.send_command('AT+SAPBR=0,1')
        s = self.ser.read(size=1024)

        self.send_command('AT+SAPBR=1,1')
        s = self.ser.read(size=1024)

        self.send_command('AT+SAPBR=2,1')
        s = self.ser.read(size=1024)
        ip = s.decode().split('"')[1]

        self.send_command('AT+CIPGSMLOC=1,1')
        s = ''
        while 'OK' not in s:
            s = self.ser.read(size=1024).decode()
        print('location: ', s)

        self.send_command('ATZ')
        s = self.ser.read(size=1024)

        return({"ip": ip, "lat": None, "lng": None})
