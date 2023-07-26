import requests
import json
import hashlib
import datetime
import time
import mysql.connector

url="http://192.168.1.160/data"

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="tiempo"
)
cursor = mydb.cursor()

def calcularHash(data):
    md5Hash = hashlib.md5()
    md5Hash.update(data)
    return md5Hash.hexdigest()

hashAnterior = None

while True:
    respuesta = requests.get(url)
    datos = respuesta.json()

    hashActual = calcularHash(respuesta.content)

    print(datos)

    if (hashActual != hashAnterior):
        hashAnterior = hashActual
        print("Los datos han cambiado")
    
        ahora = datetime.datetime.now()

        fecha = ahora.strftime("%Y-%m-%d %H:%M")
        temperatura = datos['temperatura']
        presion = datos['presion']
        humedad = datos['humedad']
        velocidad = datos['velocidad']
        direccion = datos['direccion']
        precipitaciones = datos['precipitaciones']
        uvi = datos['uvi']
        luxes = datos['luxes']
        ppm = datos['ppm']

        sql = "INSERT INTO mediciones (fecha, temperatura, humedad, presion, precipitaciones, velocidad, direccion, uvi, lux, ppm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (fecha, temperatura, humedad, presion, precipitaciones, velocidad, direccion, uvi, luxes, ppm)
        cursor.execute(sql, val)
        mydb.commit()
    
    else:
        print("Los datos no han cambiado")
    
    time.sleep(30)
        