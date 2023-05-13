import asyncio
import board
import keypad

agua = 0
radio = 9.0
intervalo = 10
ajuste = 1.18
limite = 1000

def pluviometria():
    global agua
    agua += 1
    print("Agua: ",agua)

# def resetPluviometria()
#     global agua
#     agua = 0
    
def calcularMM():
    global agua
    mm = agua * 0.2794
    return mm

async def catch_pin_transitions(pin):
    """Print a message when pin goes low and when it goes high."""
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.released:
                    pluviometria()
            await asyncio.sleep(0)

async def principal():
    while True:
        global intervalo
        global agua
        agua = 0
        await asyncio.sleep(intervalo)
        print(calcularMM(), "mm")
        

async def main():
    interrupt_task = asyncio.create_task(catch_pin_transitions(board.GP21))
    print_task = asyncio.create_task(principal())
    await asyncio.gather(interrupt_task, print_task)

asyncio.run(main())


