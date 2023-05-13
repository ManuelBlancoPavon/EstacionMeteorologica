import asyncio
import board
import keypad
import math

vueltas = 0
radio = 9.0
intervalo = 15
ajuste = 1.18
limite = 1000

def calcularVelocidad(tiempo):
    global vueltas
    circunferencia = (2 * math.pi) * radio
    rotaciones = vueltas / 2.0
    
    distKM = (circunferencia * rotaciones) / 100000
    
    kms = distKM / tiempo
    kmh = kms * 3600
    
    return kmh * ajuste

async def catch_pin_transitions(pin):
    """Print a message when pin goes low and when it goes high."""
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.released:
                    global vueltas
                    vueltas += 1
                    print("Vuelta", vueltas)
            await asyncio.sleep(0)

async def principal():
    while True:
        global vueltas
        global intervalo
        vueltas = 0
        await asyncio.sleep(intervalo)
        print(calcularVelocidad(intervalo), "km/h")
        

async def main():
    interrupt_task = asyncio.create_task(catch_pin_transitions(board.GP22))
    print_task = asyncio.create_task(principal())
    await asyncio.gather(interrupt_task, print_task)

asyncio.run(main())

