Raspi-io
========
Using websocket remote control your raspberry pi, raspberry pi needs create an  [RaspiIOServer](https://github.com/amaork/raspi-ios "RaspiIOServer") instance.

## Features

- Support Python 2.7+, Python3+
- Support I2C, API same as [pylibi2c](https://github.com/amaork/libi2c)
- Support GPIO、Software PWM, API same as [RPi.GPIO](https://sourceforge.net/projects/raspberry-gpio-python/)
- Support query raspi hardware information, such as: Serial No.、MAC address, device list etc

## Installation

1. First install [raspi-ios](https://github.com/amaork/raspi-ios) on your raspberry pi, and create an `RaspiIOServer` instance

2. Second install `raspi-io` on your computer, `sudo python setup.py install`

## Default port

`raspi_io` default using port **`9876`** communicate with [RaspiIOServer](https://github.com/amaork/raspi-ios "RaspiIOServer"), but if `RaspiIOServer` port changed, your can specify default port like this:

    import raspi_io
    raspi_io.core.DEFAULT_PORT = xxxx


## Interface

    Query: query raspi info

    GPIO: usage same as RPi.GPIO

    SoftPWM: usage same as RPi.GPIO.PWM

    Serial: support read/write/close/flushInput/flushOutput

    I2C: support open/read/write/ioctl_read/ioctl_write

## I2C Usage

    import ctypes
    from raspi_io import I2C

    # Open /dev/i2c-1, you can using Query.get_i2c_list() get i2c bus list
    i2c = I2C('192.168.1.166', '/dev/i2c-1', 0x56)

    # Python2, 3, both can using ctypes.create_string_buffer() create a buffer
    buf = ctypes.create_string_buffer(256)

    # Python3 can using bytes, create a buffer
    buf = bytes(256)

    # Write
    if i2c.write(0x0, buf) != len(buf):
        # Error process
        pass

    # Read from i2c, Python2 return str, Python3 return bytes
    r_buf = i2c.read(0x0, 256)

## GPIO Usage

    from raspi_io import GPIO

    # Create a gpio instance
    gpio = GPIO('192.168.1.166')

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
    pwm = SoftPWM('192.168.1.166', GPIO.BCM, 21, 1000)

    # Start pwm duty
    pwm.start(80)

    # Stop
    pwm.stop()

## Serial usage

    from raspi_io import Serial

    # Open a serial port /dev/ttyUSB0, 115200 baudrate
    port = Serial('192.168.1.166', '/dev/ttyUSB0', 115200)

    # Read
    ret, data = port.read(1024)
    if not ret:
        print("Read error:{}".format(data))

    # Write
    ret, data = port.write("1234567")
    if not ret:
        print("Write error:{}".format(data))
    else:
        print("Success write:{} bytes".format(data))

    # Close
    port.close()

## Query usage

    from raspi_io import Query

    # Create a query instance
    q = Query("192.168,1,166")

    # Get hardware information
    info = q.get_hardware_info()

    # Error process
    if not info:
        pass

    hardware, revision, sn = info

    # Get seril port list
    l = q.get_serial_list()

