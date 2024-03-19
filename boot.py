# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)

import webrepl
webrepl.start()

import sx127x
import time
import _thread
from neo6m import Neo6mGPS
from machine import Pin, I2C, UART
from wifi_manager import WiFiManager
from ssd1306 import SSD1306_I2C

SSID = "JioThings"
PSK = "jio12345"

wm = WiFiManager()
wm.connect(SSID,PSK)

i2c = I2C(sda=Pin(21), scl=Pin(22))
display = SSD1306_I2C(128, 64, i2c)

uart = UART(2, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

def show_ip():
    rssi = wm.get_rssi()
    display.fill(0)
    display.text(SSID, 0, 0, 1)
    display.text('RSSI: '+str(rssi), 0, 10, 1)
    display.text(wm.get_ip(), 0, 20, 1)
    
def GPSThread():
    while True:
        data = uart.read()
        if data != None:
            try:
                show_ip()
                gps = Neo6mGPS(data)
                if gps.valid_loc:
                    lat = gps.latitude()
                    lng = gps.longitude()
                    if lat != None and lng != None:
                        display.text("Lat : "+gps.latitude(), 0, 30, 1)
                        display.text("Lng : "+gps.longitude(), 0, 40, 1)
                if gps.valid_time:
                    hour = gps.hour()
                    minute = gps.minute()
                    sec = gps.sec()
                    t = hour+":"+minute+":"+sec
                    if hour != None and minute != None and sec != None:
                        display.text(t, 0, 50, 1)
                display.show()
            except Exception as err:
                print(err)
        time.sleep(1)
show_ip()
display.show()
_thread.start_new_thread(GPSThread, ())