#!/usr/bin/env python3.5

from raspi_io import GPIO


if __name__ == "__main__":
    io = [20, 21]
    gpio = GPIO("192.168.1.166")

    gpio.setmode(GPIO.BCM)
    gpio.setup(io, GPIO.OUT)

    gpio.output(io, 1)
    gpio.output(io, 0)
    gpio.output(io, [1, 0])
    gpio.output(io, [0, 1])

    gpio.setup(21, GPIO.IN, GPIO.PUD_DOWN)
    print(gpio.input(21))
    print(gpio.input(21))
    print(gpio.input(21))
