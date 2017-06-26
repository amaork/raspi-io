Raspi-io
========
Using websocket control your raspberry pi, raspberry pi needs run a [RaspiIOServer](https://github.com/amaork/raspi-ios "RaspiIOServer").

## Features

- Support Python 2.7+, Python3+
- Support GPIO、Software PWM, API same as RPi.GPIO

## Interface

    GPIO: usage same as RPi.GPIO, but needs a address (host, port) 
    
    SoftPWM: usage same as RPi.GPIO.PWM, but needs a address (host, port)
    
## GPIO Usage

    from raspi_io import GPIO
    
    # Create a gpio instance
    gpio = GPIO(('192.168.1.100', 12345))
    
    # Set as BCM mode
    gpio.setmode(GPIO.BCM)
    
    # Setup pin 21 as output, 20 as input
    gpio.setup(21, GPIO.OUT)
    gpio.setup(20, GPIO.IN)
    
    # Output control
    gpio.output(21, 1)
    gpio.output(21, 0)
    
    # Get input
    print(gpio.input(20))
    
## SoftPWM usage

    from raspi_io import GPIO, SoftPWM
    
    # Create a software pwm instance, BCM mode, pin21, 1000hz
    pwm = SoftPWM(('192.168.1.100', 12345), GPIO.BCM, 21, 1000)
    
    # Start pwm duty
    pwm.start(80)
    
    # Stop
    pwm.stop()
  


