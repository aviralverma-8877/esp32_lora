# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)

import os
import time
import _thread
from neo6m import Neo6mGPS
import machine
from machine import Pin, I2C, UART
from wifi_manager import WiFiManager
from ssd1306 import SSD1306_I2C
from lora import lora

led = Pin(2, Pin.OUT)
pir = Pin(39, Pin.IN)
l = Pin(36, Pin.IN)

SSID = "WiFi_SSID"
PSK = "*******"
WIFI_CONNECT = False

WM = WiFiManager()
if WIFI_CONNECT:
    WM.connect(SSID,PSK)
    import webrepl
    webrepl.start()
i2c = I2C(sda=Pin(21), scl=Pin(22))
display = SSD1306_I2C(128, 64, i2c)

uart = UART(2, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

POS = {"Type":"loc","ID":str(machine.unique_id())}
RX = False
TX = False

def show_ip():
    global WIFI_CONNECT
    global WM
    if WIFI_CONNECT:
        rssi = WM.get_rssi()
        display.fill(0)
        display.text(SSID, 0, 0, 1)
        display.text('RSSI: '+str(rssi), 0, 10, 1)
        display.text(WM.get_ip(), 0, 20, 1)
    else:
        display.fill(0)
        display.text("Not Connected", 0, 0, 1)

def handle_interrupt(pin):
    transmit_loc()

def req_loc(pin):
    try:
        global TX
        TX = True
        payload = {"Type":"req_loc"}
        lora.println(str(payload))
        TX = False
    except Exception as e:
        print(e)

def transmit_loc():
    try:
        global TX
        TX = True
        lora.println(str(POS))
        display.fill(0)
        display.text("LORA TX",0,0,1)
        display.show()
        TX = False
    except Exception as e:
        print(e)

def GPSThread():
    while True:
        global RX
        global TX
        if TX == False and RX == False:
            data = uart.read()
            if data != None:
                try:
                    show_ip()
                    gps = Neo6mGPS(data)
                    global POS
                    if gps.valid_loc:
                        lat = gps.latitude()
                        lng = gps.longitude()
                        if lat != None and lng != None:
                            display.text("Lat : "+gps.latitude(), 0, 30, 1)
                            display.text("Lng : "+gps.longitude(), 0, 40, 1)
                            POS["Lat"] = gps.latitude()
                            POS["Lng"] = gps.longitude()
                    if gps.valid_time:
                        hour = gps.hour()
                        minute = gps.minute()
                        sec = gps.sec()
                        t = hour+":"+minute+":"+sec
                        if hour != None and minute != None and sec != None:
                            display.text(t, 0, 50, 1)
                            POS["Time"] = hour+":"+minute+":"+sec
                    display.show()
                except Exception as err:
                    print(err)
        time.sleep(1)

def receive():
    while True:
        if lora.receivedPacket():
            try:
                global RX
                RX = True
                payload = lora.readPayload().decode()
                lora.collectGarbage()
                rssi = lora.packetRssi()
                display.fill(0)
                display.text("LORA RX", 0, 0, 1)
                res = eval(payload)
                if "Type" in res:
                    if res["Type"] == "loc":
                        record = open("record.txt", "a")
                        record.write(str(res)+"\r\n")
                        record.close()
                        if "Time" in res:
                            display.text(res["Time"], 0, 10, 1)
                        if "Lat" in res:
                            display.text(res["Lat"], 0, 20, 1)
                        if "Lng" in res:
                            display.text(res["Lng"], 0, 30, 1)
                        display.text("RSSI: "+str(rssi), 0, 40, 1)
                        display.show()
                        time.sleep(1)
                    elif res["Type"] == "req_loc":
                        transmit_loc()
                RX = False
            except Exception as e:
                print(e)
show_ip()
display.show()
pir.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)
l.irq(trigger=Pin.IRQ_FALLING, handler=req_loc)
_thread.start_new_thread(GPSThread, ())
_thread.start_new_thread(receive, ())