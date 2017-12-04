import unittest
from raspi_io import Serial, Query
from raspi_io.utility import scan_server


class TestSerial(unittest.TestCase):
    def setUp(self):
        address = scan_server(timeout=0.03)[0]
        query = Query(address)
        name_list = query.get_serial_list()
        self.serial_list = [Serial(address, name, 115200, verbose=0) for name in name_list]

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
        for port in self.serial_list:
            self.assertEqual(port.write(str_data.encode('utf-8')), len(str_data))


if __name__ == "__main__":
    unittest.main()
