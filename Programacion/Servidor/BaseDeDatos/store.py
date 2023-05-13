import requests
import json
import datetime
import time
import mysql.connector

respuesta = requests.get('http://192.168.1.160/data')

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="tiempo"
)
cursor = mydb.cursor()

while True:
    data = json.loads(respuesta.text)
    ahora = datetime.datetime.now()

    fecha = ahora.strftime("%Y-%m-%d %H:%M")
    temperatura = data['temperatura']
    presion = data['presion']
    humedad = data['humedad']
    velocidad = data['velocidad']
    direccion = data['direccion']
    precipitaciones = data['precipitaciones']
    uvi = data['uvi']
    luxes = data['luxes']
    ppm = data['ppm']

    sql = "INSERT INTO mediciones (fecha, temperatura, humedad, presion, precipitaciones, velocidad, direccion, uvi, lux, ppm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (fecha, temperatura, humedad, presion, precipitaciones, velocidad, direccion, uvi, luxes, ppm)
    cursor.execute(sql, val)
    mydb.commit()

    print(fecha)
    print(data)
    time.sleep(300)
    # print(temperatura, presion, humedad, velocidad, direccion, precipitaciones, uvi, luxes, ppm)
