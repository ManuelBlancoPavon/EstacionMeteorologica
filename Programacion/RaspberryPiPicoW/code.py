import asyncio
import board
import keypad
import time
import math
import analogio
import busio
import os
import adafruit_ltr390
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.mime_type import MIMEType
import ipaddress
import wifi
import adafruit_datetime
import json
import socketpool
import adafruit_requests
import microcontroller

## Variables
# Wifi
ipv4 =  ipaddress.IPv4Address("192.168.1.160")
netmask =  ipaddress.IPv4Address("255.255.255.0")
gateway =  ipaddress.IPv4Address("192.168.1.1")
wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)

ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")

while True:
    try:
        print("Connecting to", ssid)
        wifi.radio.connect(ssid, password)
        print("Connected to", ssid)
        ipv4 = ipaddress.ip_address("8.8.8.8")
        print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))
        break
    except Exception as e:
        print("Error:\n", str(e))
        time.sleep(40)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool, "/static")

url = "http://worldtimeapi.org/api/timezone/Europe/Madrid"
requests = adafruit_requests.Session(pool)
# Pluviometro
agua = 0
# Anemometro
vueltas = 0
radio = 9.0
intervalo = 900
ajuste = 1.18
limite = 1000
# Veleta
volts = {0.4: 0,
         2.8: 90,
         1.8: 180,
         0.1: 270,
         1.2: 45,
         2.3: 135,
         0.8: 225,
         0.2: 315,
         1.4: 22.5,
         2.9: 112.5,
         2.6: 157.5,
         2.0: 202.5,
         0.7: 247.5,
         0.3: 292.5,
         0.6: 337.5}

## Sensores
# MQ-135
MQ135 = analogio.AnalogIn(board.GP27)
# BME280
i2c = busio.I2C(board.GP1, board.GP0)  # SCL, SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
# LTR390
i2c = busio.I2C(board.GP3, board.GP2)  # SCL, SDA
ltr390 = adafruit_ltr390.LTR390(i2c)
# Veleta
analog_value = analogio.AnalogIn(board.GP26)

### Codigo
## Wifi
# Conectarse a la red

print(f"Listening on http://{wifi.radio.ipv4_address}:80")
server.start(str(wifi.radio.ipv4_address))
def calcularMM():
    global agua
    mm = agua * 0.2794
    return mm

def calcularVelocidad(tiempo):
    global vueltas
    circunferencia = (2 * math.pi) * radio
    rotaciones = vueltas / 2.0
    
    distKM = (circunferencia * rotaciones) / 100000
    
    kms = distKM / tiempo
    kmh = kms * 3600
    
    return kmh * ajuste

def calcularppm():
    calibracion = 0.00322265625
    valorBruto = MQ135.value
    voltaje = valorBruto * 3.3 / 65536
    ppm = voltaje / calibracion
    return ppm

async def catch_pin_transitions2(pin):
    """Print a message when pin goes low and when it goes high."""
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.released:
                    global agua
                    agua += 1
            await asyncio.sleep(0)

async def catch_pin_transitions(pin):
    """Print a message when pin goes low and when it goes high."""
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.released:
                    global vueltas
                    vueltas += 1
            await asyncio.sleep(0)
velocidad = 0
ppm = 0
direccion = 0
temperatura = 0
humedad = 0
presion = 0
precipitaciones = 0
uvi = 0
lux = 0

async def principal():
    while True:
        try:
            global vueltas
            global agua
            global intervalo
            global velocidad
            global ppm
            global direccion
            global temperatura
            global humedad
            global presion
            global precipitaciones
            global uvi
            global lux
            agua = 0
            vueltas = 0
            await asyncio.sleep(intervalo)
            ppm = calcularppm()
            temperatura = bme280.temperature
            humedad = bme280.relative_humidity
            presion = bme280.pressure
            precipitaciones = calcularMM()
            uvi = ltr390.uvi
            lux = ltr390.lux
            velocidad = calcularVelocidad(intervalo)
            voltios = round((analog_value.value * 3.33333) / 65535, 1)
            print("Velocidad del viento", velocidad, "km/h")
            print("Temperatura: %0.1f C" % bme280.temperature)
            print("Humedad: %0.1f %%" % bme280.relative_humidity)
            print("Presion: %0.1f hPa" % bme280.pressure)
            print("Precipitaciones: ", calcularMM(), "mm")
            print("Indice de radiacion UV:", ltr390.uvi)
            print("Luxes: ", ltr390.lux, "iluminancia")
            print("Concentracion de gases: %.2f ppm" % ppm)
            if not voltios in volts:
                direccion = -1
                print("Direccion del viento desconocida")
            else:
                direccion = str(volts[voltios])
                print("Direccion del viento: " + str(volts[voltios]))
                
        except Exception as e:
            print("Error en principal")
            time.sleep(5)
            microcontroller.reset()

async def updateServer():
    timer = 0
    while True:
        try:
            print(timer)
            await asyncio.sleep(0.5)
            timer += 0.5
            server.poll()
        except Exception as e:
            print("Error en enviando los datos")
            time.sleep(5)
            microcontroller.reset()
        
@server.route("/data") 
def cpu_information_handler(request: HTTPRequest):
    try:
        global velocidad
        global ppm
        global direccion
        global temperatura
        global humedad
        global presion
        global precipitaciones
        global uvi
        global lux
        data = {
            "velocidad": round(velocidad, 2),
            "temperatura": round(temperatura, 2),
            "humedad": round(humedad, 2),
            "presion": round(presion, 2),
            "precipitaciones": round(precipitaciones, 2),
            "uvi": round(uvi, 2),
            "luxes": round(lux, 2),
            "direccion": direccion,
            "ppm": round(ppm, 2)
        }

        with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
            response.send(json.dumps(data))
            
    except Exception as e:
        print("Error actualizando los datos")
        time.sleep(5)
        microcontroller.reset()

async def main():
    interrupt_task = asyncio.create_task(catch_pin_transitions(board.GP22))
    interrupt_task2 = asyncio.create_task(catch_pin_transitions2(board.GP21))
    server_task = updateServer()
    print_task = asyncio.create_task(principal())
    check_internet = asyncio.create_task(comprobarInternet())
    await asyncio.gather(interrupt_task, interrupt_task2, print_task, server_task, check_internet)

async def comprobarInternet():
    while True:
        try:
            await asyncio.sleep(300)
            ipv4 = ipaddress.ip_address("8.8.8.8")
            print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))
        except Exception as e:
            print("Se ha ido la conexion a internet")
            time.sleep(5)
            microcontroller.reset()

while True:
    response = requests.get(url)
    jsonTiempo = response.json()
    strTiempo = jsonTiempo['datetime']
    objTiempo = adafruit_datetime.datetime.fromisoformat(strTiempo)
    minutos = objTiempo.minute
    
    if minutos % 5 == 0:
        asyncio.run(main())
        break  # Salir del bucle después de llamar a asyncio.run(main())
    
    # Si minutos % 5 no es igual a 0, esperar y volver a intentarlo
    time.sleep(5)