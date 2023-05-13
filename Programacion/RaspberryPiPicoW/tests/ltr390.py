# SPDX-FileCopyrightText: 2021 by Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
import adafruit_ltr390
import busio
import board

i2c = busio.I2C(board.GP3, board.GP2)  # SCL, SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
ltr = adafruit_ltr390.LTR390(i2c)

while True:
    # print("UV:", ltr.uvs, "\t\tAmbient Light:", ltr.light)
    print("UV Index:", ltr.uvi, "\t\tLux:", ltr.lux)
    time.sleep(1.0)
