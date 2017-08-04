import six
import ctypes
import unittest
from raspi_io import Serial, Query


class TestSerial(unittest.TestCase):
    def setUp(self):
        query = Query('192.168.1.166')
        name_list = query.get_serial_list()
        self.serial_list = [Serial('192.168.1.166', name, 115200, verbose=0) for name in name_list]

    def tearDown(self):
        del self.serial_list

    def test_open(self):
        for port in self.serial_list:
            self.assertEqual(port.is_open, True)

    def test_read(self):
        for port in self.serial_list:
            self.assertEqual(port.read(1), "")
            self.assertEqual(port.read(100), "")

    def test_write(self):
        str_data = "12345678"
        bin_data = ctypes.create_string_buffer(8)
        for i in range(8):
            bin_data[i] = six.int2byte(i)
        for port in self.serial_list:
            self.assertEqual(port.write(str_data.encode('utf-8')), len(str_data))
            self.assertEqual(port.write(bin_data), len(bin_data))


if __name__ == "__main__":
    unittest.main()
