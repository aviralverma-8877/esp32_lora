class Neo6mGPS:
    def __init__(self, data):
        self.valid_loc = True
        self.valid_time = True
        self.lat = None
        self.long = None
        self.hr = None
        self.mn = None
        self.sc = None
        if data != None:
            data = str(data).split('\\r\\n')
            if len(data) >= 3:
                self.GPRMC = data[0]
                self.GPGGA = data[1]
                self.GPGSA = data[2]
                self.gpgga_data = self.GPGGA.split(",")
                if self.gpgga_data[6] == '0' or self.gpgga_data[7] == '00':
                    self.valid_loc = False
                if self.gpgga_data[1] == "":
                    self.valid_time = False
                if self.valid_time:
                    self.decode_time()
                if self.valid_loc:
                    self.decode_location()
            return
        else:
            self.valid_loc = False
            self.valid_time = False
            return

    def decode(self, coord):
        l = float(coord)/100
        return str(l)

    def decode_time(self):
        if self.valid_time:
            self.hr = self.gpgga_data[1][0:2]
            self.mn = self.gpgga_data[1][2:4]
            self.sc = self.gpgga_data[1][4:6]
    
    def decode_location(self):
        if self.valid_loc:
            self.lat = self.decode(self.gpgga_data[2])
            self.long = self.decode(self.gpgga_data[4])
    
    def latitude(self):
        if self.valid_loc:
            return self.lat
    
    def longitude(self):
        if self.valid_loc:
            return self.long
    
    def hour(self):
        if self.valid_time:
            return self.hr
    
    def minute(self):
        if self.valid_time:
            return self.mn
    
    def sec(self):
        if self.valid_time:
            return self.sc
    
    def day(self):
        pass
    
    def month(self):
        pass
    
    def year(self):
        pass

