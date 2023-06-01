from flask import Flask, render_template, render_template_string, request, send_from_directory, url_for
import mysql.connector
from jinja2 import Environment
import plotly.graph_objects as go
import datetime

app = Flask(__name__)
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="tiempo"
)

# routes
@app.route('/', methods=['GET', 'POST'])
def bar():
    #diaDefault = (2023, 5, 15)
    #diaBuscar = datetime.date(*diaDefault)
    horaInicio = "00:00:00"
    horaFin = "23:59:59"
    diaBuscar = datetime.date.today()
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
    mydb.commit()
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
    
    # Calcular maximos y minimos
    tempMax = max(temperatura)
    tempMin = min(temperatura)
    humMax = max(humedad)
    humMin = min(humedad)
    presMax = max(presion)
    presMin = min(presion)
    velMax = max(velocidad)
    velMin = min(velocidad)
    velMedia = round(sum(velocidad)/len(velocidad), 2)
    uvMax = max(uv)
    uvMin = min(uv)
    mmTotal = round(sum(precipitaciones), 2)

    env = Environment()
    env.globals.update(zip=zip)
    return render_template("index.html", tempMax=tempMax, tempMin=tempMin, humMax=humMax, humMin=humMin, presMax=presMax,
                           presMin=presMin, mmTotal=mmTotal, temperaturas=temperatura,uvs=uv,luxes=lux,ppms=ppm,direcciones=direccion,
                           humedades=humedad, presiones=presion, precipitaciones=precipitaciones, velocidades=velocidad,fechas=fechaFormateada,
                           dia=diaBuscarFormateado,horax=horaInicio,horay=horaFin, zip=zip)

@app.route('/graficos', methods=['GET', 'POST'])
def graficos():
    diaDefault = (2023, 5, 15)
    diaBuscar = datetime.date(*diaDefault)
    horaInicio = "00:00:00"
    horaFin = "23:59:59"
    diaMax = diaBuscar
    diaMin = diaBuscar
    # diaBuscar = datetime.date.today()
    if request.method == 'POST':
        diaMax = request.form['desdeDia']
        mesMax = request.form['desdeMes']
        anoMax = request.form['desdeAno']
        diaMin = request.form['hastaDia']
        mesMin = request.form['hastaMes']
        anoMin = request.form['hastaAno']
        
        try:
            diaOBJ = datetime.datetime.strptime(diaMax, '%d')
            diaSaneado = diaOBJ.strftime('%d')
            diaProcesar = int(diaSaneado)

            mesOBJ = datetime.datetime.strptime(mesMax, '%M')
            mesSaneado = mesOBJ.strftime('%M')
            mesProcesar = int(mesSaneado)

            anoOBJ = datetime.datetime.strptime(anoMax, '%Y')
            anoSaneado = anoOBJ.strftime('%Y')
            anoProcesar = int(anoSaneado)

            diaMax = datetime.date(anoProcesar, mesProcesar, diaProcesar)

            diaOBJ = datetime.datetime.strptime(diaMin, '%d')
            diaSaneado = diaOBJ.strftime('%d')
            diaProcesar = int(diaSaneado)

            mesOBJ = datetime.datetime.strptime(mesMin, '%M')
            mesSaneado = mesOBJ.strftime('%M')
            mesProcesar = int(mesSaneado)

            anoOBJ = datetime.datetime.strptime(anoMin, '%Y')
            anoSaneado = anoOBJ.strftime('%Y')
            anoProcesar = int(anoSaneado)

            diaMin = datetime.date(anoProcesar, mesProcesar, diaProcesar)
            
        except ValueError:
            return 'La fecha introducida no es válida.'
        
    mycursor = mydb.cursor()
    consulta = """
    SELECT fecha, temperatura, humedad, presion, precipitaciones, velocidad, direccion, uvi, lux, ppm 
    FROM mediciones 
    WHERE DATE(fecha) >= %s
    AND DATE(fecha) <= %s
    AND TIME(`fecha`) >= %s
    AND TIME(`fecha`) <= %s
    ORDER BY fecha DESC
    """
    mycursor.execute(consulta, (diaMax, diaMin, horaInicio, horaFin))
    resultado = mycursor.fetchall()
    mydb.commit()
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

    # --------------------------- Graficos -------------------------------

    # Crear los objetos
    tablaTemperaturas = go.Scatter(x=fecha, y=temperatura, mode='lines', marker=dict(color='red'))
    tablaHumedades = go.Scatter(x=fecha, y=humedad, mode='lines', marker=dict(color='blue'))
    tablaPresiones = go.Scatter(x=fecha, y=presion, mode='lines', marker=dict(color='green'))
    tablaVelocidades = go.Bar(x=fecha, y=velocidad, marker=dict(color='orange'))
    tablaDirecciones = go.Bar(x=fecha, y=direccion, marker=dict(color='gray'))
    tablaPrecipitaciones = go.Bar(x=fecha, y=precipitaciones, marker=dict(color='blue'))
    tablaUVS = go.Scatter(x=fecha, y=uv, mode='lines', marker=dict(color='violet'))
    tablaPPM = go.Scatter(x=fecha, y=ppm, mode='lines', marker=dict(color='black'))
    tablaLuxes = go.Scatter(x=fecha, y=lux, mode='lines', marker=dict(color='green'))

    # Crear las figuras
    figTemperaturas = go.Figure(data=[tablaTemperaturas], layout=go.Layout(title="Gráfico de temperaturas (ºC)"))
    figHumedades = go.Figure(data=[tablaHumedades], layout=go.Layout(title="Gráfico de humedades (%)"))
    figPresiones = go.Figure(data=[tablaPresiones], layout=go.Layout(title="Gráfico de presiones (hPa)"))
    figVelocidades = go.Figure(data=[tablaVelocidades], layout=go.Layout(title="Gráfico de velocidades (km/h)"))
    figDirecciones = go.Figure(data=[tablaDirecciones], layout=go.Layout(title="Gráfico de direcciónes del viento (º)"))
    figPrecipitaciones = go.Figure(data=[tablaPrecipitaciones], layout=go.Layout(title="Gráfico de precipitaciones (mm)"))
    figUVS = go.Figure(data=[tablaUVS], layout=go.Layout(title="Gráfico de índice UV (Índice de UV)"))
    figPPM = go.Figure(data=[tablaPPM], layout=go.Layout(title="Gráfico de calidad del aire (ppm)"))
    figLuxes = go.Figure(data=[tablaLuxes], layout=go.Layout(title="Gráfico de luxes (lux)"))


    # Obtener el HTML para ambos gráficos
    graficoTemperaturas = figTemperaturas.to_html(full_html=False)
    graficoHumedades = figHumedades.to_html(full_html=False)
    graficoPresiones = figPresiones.to_html(full_html=False)
    graficoVelocidades = figVelocidades.to_html(full_html=False)
    graficoDirecciones = figDirecciones.to_html(full_html=False)
    graficoPrecipitaciones = figPrecipitaciones.to_html(full_html=False)
    graficoUVS = figUVS.to_html(full_html=False)
    graficoPPM = figPPM.to_html(full_html=False)
    graficoLuxes = figLuxes.to_html(full_html=False)

    # Renderizar los gráficos en la plantilla
    return render_template('graficos.html', temperaturas=graficoTemperaturas, humedades=graficoHumedades, presiones=graficoPresiones, velocidades=graficoVelocidades, direcciones=graficoDirecciones, precipitaciones=graficoPrecipitaciones, uvs=graficoUVS, ppms=graficoPPM, luxes=graficoLuxes, diaMax=diaMax,diaMin=diaMin)


if __name__ == "__main__":
    # Development
    # app.run(port=8080, debug=True, host='192.168.1.40')
    # Production
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)