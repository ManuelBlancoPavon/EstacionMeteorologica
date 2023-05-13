import time
import board
import analogio

# Configuración del pin analógico
analog_in = analogio.AnalogIn(board.GP27)

# Factor de conversión para obtener la concentración de gas en ppm
# Este factor debe ser ajustado para el tipo de gas que se está midiendo y la tensión de alimentación
# Aquí se utiliza el factor para medir concentración de CO2 con una fuente de alimentación de 3.3V
CALIBRATION_FACTOR = 0.00322265625

while True:
    # Leer el valor analógico del sensor
    raw_value = analog_in.value

    # Convertir el valor analógico a voltaje
    voltage = raw_value * 3.3 / 65536

    # Calcular la concentración de gas en ppm
    gas_concentration = voltage / CALIBRATION_FACTOR

    # Imprimir la concentración de gas en ppm
    print("Raw value: ", raw_value)
    print("Voltaje: ", voltage)
    print("Concentración de CO2: %.2f ppm" % gas_concentration)

    # Esperar 1 segundo antes de volver a leer el sensor
    time.sleep(1)
