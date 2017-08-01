#!/usr/bin/env python3.5
import six
import ctypes
from raspi_io import I2C


if __name__ == '__main__':
    i2c = I2C('192.168.1.166', '/dev/i2c-1', 0x56)
    # Python 3+ version can using bytes
    buf = ctypes.create_string_buffer(256)
    for i in range(256):
        buf[i] = six.int2byte(i)

    # Write
    print("Write {} bytes".format(i2c.write(0x0, buf)))

    # Read
    data = i2c.read(0x0, 256)
    print("Read {} bytes".format(len(data)))

    # Should be 0 and 255
    print(data[0], data[255])

