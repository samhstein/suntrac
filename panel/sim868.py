import serial

class sim868:

    ser = None

    def __init__(self,):
        print("in itis")
        try:
            self.ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
            self.ser.close()
        except Exception as e:
            print("can't open serial device")

    def open(self):
            self.ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)

    def send_command(self, command):
        with_return = str(command) + '\n'
        self.ser.write(with_return.encode('utf-8'))

    def get_status(self):
        print('in get_status')
        self.ser.open()
        self.send_command('ATZ')
        s = self.ser.read(size=1024)

        self.send_command('AT+CCID')
        s = self.ser.read(size=1024)
        iccid = s.decode().split('\r\n')[1]

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
        point = s.split(',')
        try:
            lat = point[2]
            lng = point[1]
        except:
            lat = 'n/a'
            lng = 'n/a'

        self.send_command('ATH')
        s = self.ser.read(size=1024)

        self.send_command('ATH')
        s = self.ser.read(size=1024)

        self.send_command('ATZ')
        s = self.ser.read(size=1024)

        self.ser.close()
        print('end of get status')

        return({"iccid": iccid, "ip": ip, "lat": lat, "lng": lng})
