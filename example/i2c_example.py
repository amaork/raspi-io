#!/usr/bin/env python3.5
from raspi_io import I2C
import raspi_io.utility as utility


if __name__ == '__main__':
    i2c = I2C(utility.scan_server()[0], '/dev/i2c-1', 0x56)
    # Write
    print("Write {} bytes".format(i2c.write(0x0, list(range(256)))))

    # Read
    data = i2c.read(0x0, 256)
    print("Read {} bytes".format(len(data)))

    # Should be 0 and 255
    i2c.print_binary(data, 16)
    print(data[0], data[255])
