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
    diaDefault = (2023, 5, 15)
    diaBuscar = datetime.date(*diaDefault)
    horaInicio = "00:00:00"
    horaFin = "23:59:59"
    # diaBuscar = datetime.date.today()
    if request.method == 'POST':
        diaIntroducido = request.form['dia']
        mesIntroducido = request.form['mes']
        anoIntroducido = request.form['ano']
        horax = request.form['horax']
        horay = request.form['horay']

        if not diaIntroducido or not mesIntroducido or not anoIntroducido:
            return 'Por favor, introduce una fecha.'
        if horax or horay:
            try:
                datetime.datetime.strptime(horax, "%H:%M")
                horaInicio = horax + ":00"
            except ValueError:
                return("Formato de hora inicio incorrecto. Debe ser en formato HH:MM.")
            try:
                datetime.datetime.strptime(horay, "%H:%M")
                horaFin = horay + ":59"
            except ValueError:
                return("Formato de hora fin incorrecto. Debe ser en formato HH:MM.")
        
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
    consulta = """
    SELECT fecha, temperatura, humedad, presion, precipitaciones, velocidad, direccion, uvi, lux, ppm 
    FROM mediciones 
    WHERE DATE(fecha) = %s
    AND TIME(`fecha`) >= %s
    AND TIME(`fecha`) <= %s
    ORDER BY fecha DESC
    """
    mycursor.execute(consulta, (diaBuscar, horaInicio, horaFin))
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
    
    # Quitarle los segundos a la fecha
    fechaFormateada = []
    for i in fecha:
        fechaFormateada.append(i.strftime('%d-%m-%Y %H:%M'))
    
    # Quitarle los segundos a horaInicio y horaFin
    horaInicio = horaInicio[:-3]
    horaFin = horaFin[:-3]
    diaBuscarFormateado = diaBuscar.strftime("%d-%m-%Y")

    env = Environment()
    env.globals.update(zip=zip)
    return render_template("index.html", temperaturas=temperatura,uvs=uv,luxes=lux,ppms=ppm,direcciones=direccion, humedades=humedad, presiones=presion, precipitaciones=precipitaciones, velocidades=velocidad,fechas=fechaFormateada,dia=diaBuscarFormateado,horax=horaInicio,horay=horaFin, zip=zip)

@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='image/favicon.ico')
if __name__ == "__main__":
    app.run(port=5000, debug=True, host='192.168.1.40')