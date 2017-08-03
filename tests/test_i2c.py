import unittest
from raspi_io import Query, I2C


class I2CTest(unittest.TestCase):
    def setUp(self):
        query = Query('192.168.1.166')
        devices = query.get_i2c_list()
        self.assertGreaterEqual(len(devices), 1)
        self.i2c = I2C('192.168.1.166', devices[0], 0x56)
        self.i2c_size = 256

    def buf_equal_test(self, r_buf, w_buf):
        if len(w_buf) != len(r_buf):
            return False

        for i in range(len(r_buf)):
            if r_buf[i] != w_buf[i]:
                return False
        else:
            return True

    def test_read(self):
        self.assertEqual(len(self.i2c.read(0x0, 1)), 1)
        self.assertEqual(len(self.i2c.read(0x11, 3)), 3)
        self.assertEqual(len(self.i2c.read(0x0, self.i2c_size)), self.i2c_size)

    def test_write(self):
        # Create a bytes, python3+ can using bytes
        w_buf = list(range(self.i2c_size))
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
        w_buf = list(range(self.i2c_size))
        # Write to i2c device
        self.assertEqual(self.i2c.ioctl_write(0x0, w_buf), self.i2c_size)
        r_buf = bytearray(self.i2c.ioctl_read(0x0, self.i2c_size))
        self.assertEqual(self.buf_equal_test(r_buf, w_buf), True)
