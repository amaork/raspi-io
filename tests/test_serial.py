import unittest
from raspi_io import Serial, Query


class TestSerial(unittest.TestCase):
    def setUp(self):
        address = ('192.168.1.166', 9876)
        query = Query(address)
        name_list = query.get_serial_list()
        self.serial_list = [Serial(address=address, port=name, baudrate=115200, verbose=0) for name in name_list]

    def test_open(self):
        for port in self.serial_list:
            self.assertEqual(port.is_open(), True)

    def test_read(self):
        for port in self.serial_list:
            ret, error = port.read(1)
            self.assertEqual(ret, False)


if __name__ == "__main__":
    unittest.main()
