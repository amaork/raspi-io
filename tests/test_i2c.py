import six
import ctypes
import unittest
from raspi_io import Query, I2C


class I2CTest(unittest.TestCase):
    def setUp(self):
        address = ('192.168.1.166', 9876)
        query = Query(address)
        devices = query.get_i2c_list()
        self.assertGreaterEqual(len(devices), 1)
        self.i2c = I2C(address, devices[0], 0x56)
        self.i2c_size = 256

    def tearDown(self):
        del self.i2c

    def buf_equal_test(self, r_buf, w_buf):
        if len(w_buf) != len(r_buf):
            return False

        for i in range(len(r_buf)):
            if six.int2byte(r_buf[i]) != w_buf[i]:
                return False
        else:
            return True

    def test_read(self):
        self.assertEqual(len(self.i2c.read(0x0, 1)), 1)
        self.assertEqual(len(self.i2c.read(0x11, 3)), 3)
        self.assertEqual(len(self.i2c.read(0x0, self.i2c_size)), self.i2c_size)

    def test_write(self):
        # Create a bytes, python3+ can using bytes
        w_buf = ctypes.create_string_buffer(self.i2c_size)
        for i in range(self.i2c_size):
            w_buf[i] = six.int2byte(i)

        # Write to i2c device
        self.assertEqual(self.i2c.write(0x0, w_buf), self.i2c_size)
        r_buf = bytearray(self.i2c.read(0x0, self.i2c_size))
        self.assertEqual(self.buf_equal_test(r_buf, w_buf), True)

    def test_ioctl_read(self):
        self.assertEqual(len(self.i2c.ioctl_read(0x0, 1)), 1)
        self.assertEqual(len(self.i2c.ioctl_read(0x11, 3)), 3)
        self.assertEqual(len(self.i2c.ioctl_read(0x0, self.i2c_size)), self.i2c_size)

    def test_ioctl_write(self):
        # Create a bytes, python3+ can using bytes
        w_buf = ctypes.create_string_buffer(self.i2c_size)
        for i in range(self.i2c_size):
            w_buf[i] = six.int2byte(i)

        # Write to i2c device
        self.assertEqual(self.i2c.ioctl_write(0x0, w_buf), self.i2c_size)
        r_buf = bytearray(self.i2c.ioctl_read(0x0, self.i2c_size))
        self.assertEqual(self.buf_equal_test(r_buf, w_buf), True)
