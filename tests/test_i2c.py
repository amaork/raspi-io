import random
import unittest
from raspi_io import Query, I2C


class I2CTest(unittest.TestCase):
    def setUp(self):
        self.i2c_size = 256
        address = "192.168.1.166"

        query = Query(address)
        devices = query.get_i2c_list()
        self.assertGreaterEqual(len(devices), 1)
        self.i2c = I2C(address, devices[0], 0x56)

    def test_read(self):
        self.assertEqual(len(self.i2c.read(0x0, 1)), 1)
        self.assertEqual(len(self.i2c.read(0x11, 3)), 3)
        self.assertEqual(len(self.i2c.read(0x0, self.i2c_size)), self.i2c_size)

    def test_write(self):
        # Create a bytes, python3+ can using bytes
        w_buf = list(range(self.i2c_size))

        # Write ordered data to i2c device
        self.assertEqual(self.i2c.write(0x0, w_buf), self.i2c_size)
        r_buf = bytearray(self.i2c.read(0x0, self.i2c_size))
        self.assertSequenceEqual(r_buf, w_buf)

        # Write random data to i2c
        w_buf = [random.randint(0, 0xff) for _ in range(self.i2c_size)]
        self.assertEqual(self.i2c.write(0x0, w_buf), self.i2c_size)
        r_buf = bytearray(self.i2c.read(0x0, self.i2c_size))
        self.assertSequenceEqual(r_buf, w_buf)

        # Not aligned write
        for start in (1, 3, 13, 123, 113, 153):
            w_buf = [random.randint(0, 0xff) for _ in range(start, self.i2c_size)]
            self.assertEqual(self.i2c.write(start, w_buf), self.i2c_size - start)
            r_buf = bytearray(self.i2c.read(start, self.i2c_size - start))
            self.assertSequenceEqual(r_buf, w_buf)

    def test_ioctl_read(self):
        self.assertEqual(len(self.i2c.ioctl_read(0x0, 1)), 1)
        self.assertEqual(len(self.i2c.ioctl_read(0x11, 3)), 3)
        self.assertEqual(len(self.i2c.ioctl_read(0x0, self.i2c_size)), self.i2c_size)

    def test_ioctl_write(self):
        # Create a bytes, python3+ can using bytes
        w_buf = list(range(self.i2c_size))
        # Write to i2c device
        self.assertEqual(self.i2c.ioctl_write(0x0, w_buf), self.i2c_size)
        r_buf = bytearray(self.i2c.ioctl_read(0x0, self.i2c_size))
        self.assertSequenceEqual(r_buf, w_buf)

        # Write random data to i2c
        w_buf = [random.randint(0, 0xff) for _ in range(self.i2c_size)]
        self.assertEqual(self.i2c.write(0x0, w_buf), self.i2c_size)
        r_buf = bytearray(self.i2c.read(0x0, self.i2c_size))
        self.assertSequenceEqual(r_buf, w_buf)

        # Not aligned write
        for start in (1, 3, 13, 123, 113, 153):
            w_buf = [random.randint(0, 0xff) for _ in range(start, self.i2c_size)]
            self.assertEqual(self.i2c.write(start, w_buf), self.i2c_size - start)
            r_buf = bytearray(self.i2c.read(start, self.i2c_size - start))
            self.assertSequenceEqual(r_buf, w_buf)
