import os
from flask import Flask, render_template, render_template_string, request, send_from_directory, url_for
from flask_plots import Plots
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import mysql.connector
import numpy as np
from jinja2 import Environment
import datetime

app = Flask(__name__)
plots = Plots(app)
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="tiempo"
)

# routes
@app.route('/', methods=['GET', 'POST'])
def bar():
    diaDefault = (2023, 4, 27)
    diaSaneado = 27
    mesSaneado = 4
    anoSaneado = 2023
    diaBuscar = datetime.date(*diaDefault)
    # diaBuscar = datetime.date.today()
    if request.method == 'POST':
        diaIntroducido = request.form['dia']
        mesIntroducido = request.form['mes']
        anoIntroducido = request.form['ano']
        if not diaIntroducido or not mesIntroducido or not anoIntroducido:
            return 'Por favor, introduce una fecha.'
        try:
            diaOBJ = datetime.datetime.strptime(diaIntroducido, '%d')
            diaSaneado = diaOBJ.strftime('%d')
            diaProcesar = int(diaSaneado)
            mesOBJ = datetime.datetime.strptime(mesIntroducido, '%M')
            mesSaneado = mesOBJ.strftime('%M')
            mesProcesar = int(mesSaneado)
            anoOBJ = datetime.datetime.strptime(anoIntroducido, '%Y')
            anoSaneado = anoOBJ.strftime('%Y')
            anoProcesar = int(anoSaneado)
            diaBuscar = datetime.date(anoProcesar, mesProcesar, diaProcesar)
            
        except ValueError:
            return 'La fecha introducida no es válida.'
        
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT fecha, temperatura, humedad, presion, precipitaciones, velocidad, direccion, uvi, lux, ppm FROM mediciones")
    resultado = mycursor.fetchall()
    # Procesamiento de los datos
    fecha = [] # Fecha y hora 9999-99-99 99:99:99
    temperatura = [] # Temperatura en grados Celsius
    humedad = [] # Humedad relativa en porcentaje
    presion = [] # Presión atmosférica en milibares
    precipitaciones = [] # Precipitaciones en milímetros
    velocidad = [] # Velocidad del viento en kilómetros por hora
    direccion = [] # Dirección del viento en grados
    uv = [] # Índice UV
    lux = [] # Intensidad de la luz en lux
    ppm = [] # Concentración de CO2 en ppm

    for i in resultado:
        fecha.append(i[0])
        temperatura.append(i[1])
        humedad.append(i[2])
        presion.append(i[3])
        precipitaciones.append(i[4])
        velocidad.append(i[5])
        direccion.append(i[6])
        uv.append(i[7])
        lux.append(i[8])
        ppm.append(i[9])


    # print(precipitaciones)
    # Filtrar los datos para incluir solo las fechas correspondientes al día actual
    fecha_actual = [fecha[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]

    # Filtrar los datos de temperatura para incluir solo los valores correspondientes al día actual
    temperatura_actual = [temperatura[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    humedad_actual = [humedad[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    presion_actual = [presion[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    precipitaciones_actual = [precipitaciones[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    velocidad_actual = [velocidad[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    direccion_actual = [direccion[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    uv_actual = [uv[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    lux_actual = [lux[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    ppm_actual = [ppm[i] for i in range(len(fecha)) if fecha[i].date() == diaBuscar]
    env = Environment()
    env.globals.update(zip=zip)
    
    return render_template("index.html", temperaturas=temperatura_actual,uvs=uv_actual,luxes=lux_actual,ppms=ppm_actual,direcciones=direccion_actual, humedades=humedad_actual, presiones=presion_actual, precipitaciones=precipitaciones_actual, velocidades=velocidad_actual,fechas=fecha_actual, zip=zip)

@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='image/favicon.ico')
if __name__ == "__main__":
    app.run(port=5000, debug=True, host='192.168.1.38')