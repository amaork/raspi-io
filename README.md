Raspi-io
========
Using websocket control your raspberry pi, raspberry pi needs run a [RaspiIOServer](https://github.com/amaork/raspi-ios "RaspiIOServer").

## Features

- Support Python 2.7+, Python3+
- Support GPIO、Software PWM, API same as RPi.GPIO
- Support query raspi hardware information, such as: Serial No.、MAC address, device list etc

## Interface

    Query: query raspi info

    GPIO: usage same as RPi.GPIO
    
    SoftPWM: usage same as RPi.GPIO.PWM
    
    Serial: support read/write/close/flushInput/flushOutput
    
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
    
## Serial usage

    from raspi_io import Serial
    
    # Open a serial port /dev/ttyUSB0, 115200 baudrate
    port = Serial(('192.168.1.100', 12345), '/dev/ttyUSB0', 115200)
    
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
    q = Query(("192.168,1,100", 12345))
    
    # Get hardware information
    info = q.get_hardware_info()
    
    # Error process
    if not info:
        pass
        
    hardware, revision, sn = info
    
    # Get seril port list
    l = q.get_serial_list()
  