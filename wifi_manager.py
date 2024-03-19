import time
import network

class WiFiManager:
    def __init__(self):
        self.sta_if = network.WLAN(network.STA_IF)
        
    def connect(self, ssid, psk):
        if not self.sta_if.active():
            self.sta_if.active(True)
        if not self.sta_if.isconnected():
            self.sta_if.connect(ssid, psk)
            while not self.sta_if.isconnected():
                time.sleep(0.1)
        ip = self.sta_if.ifconfig()[0]
        print("Connected to "+ssid+". IP:"+ip)
    
    def get_ip(self):
        ip = self.sta_if.ifconfig()[0]
        return ip

    def get_rssi(self):
        return self.sta_if.status('rssi')
    