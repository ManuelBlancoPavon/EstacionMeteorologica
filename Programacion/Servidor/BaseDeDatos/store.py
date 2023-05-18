import requests
import json
import hashlib
import datetime
import time
import mysql.connector

url="http://192.168.1.40:5000"

respuesta = requests.get('http://192.168.1.160/data')

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="tiempo"
)
cursor = mydb.cursor()

def calcular_hash(data):
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.hexdigest()

hashAnterior = False

while True:
  response = requests.get(url)
  if response.status_code == 200:
      # Obtener los datos de la respuesta
      data = response.content
      # Calcular el hash de los datos actuales
      hashActual = calcular_hash(data)

      if hashAnterior is None:
          # Si es la primera vez, almacenar el hash actual
          hashAnterior = hashActual
      elif hashActual != hashAnterior:
          # Si el hash actual es diferente al anterior, los datos se han actualizado
          print("¡Los datos se han actualizado!")
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

          # Actualizar el hash anterior con el nuevo hash
          hashAnterior = hashActual
      else:
          print("Los datos no han cambiado")
  time.sleep(20)