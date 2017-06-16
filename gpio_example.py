from raspi_io import GPIO


if __name__ == "__main__":
    gpio = GPIO("192.168.1.166")

    gpio.setmode(GPIO.BCM)
    gpio.setup(21, GPIO.OUT)

    gpio.output(21, 1)
    gpio.output(21, 0)

    gpio.setup(21, GPIO.IN)
    print(gpio.input(21))
    print(gpio.input(21))
    print(gpio.input(21))
