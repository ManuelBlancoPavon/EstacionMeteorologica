import time
import analogio
import board

analog_value = analogio.AnalogIn(board.GP26)
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

while True:
    valor = analog_value.value # >> 6
    wind = valor*3.33333
    voltaje = wind / 65535 # 1023
    # voltios = round(voltaje, 1)
    voltios = round((analog_value.value * 3.33333) / 65535, 1)
    if not voltios in volts:
        print("Unknown value: " + str(voltios))
    else:
        print("Match: " + str(voltios) + " " + str(volts[voltios]))
    time.sleep(0.5)
