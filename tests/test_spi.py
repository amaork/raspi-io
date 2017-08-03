import unittest
from raspi_io import Query, SPI


class SPITest(unittest.TestCase):
    def setUp(self):
        address = "192.168.1.166"
        query = Query(address)
        self.spi = SPI(address, query.get_spi_list()[-1], max_speed=8000)

    def test_xfer(self):
        data = self.spi.xfer([0x9f], 3)
        self.assertEqual(len(data), 3)
        self.spi.print_binary(data)

    def test_xfer2(self):
        data = self.spi.xfer2([0x9f], 3)
        self.assertEqual(len(data), 3)
        self.spi.print_binary(data)

    def test_read(self):
        data = self.spi.read(16)
        self.assertEqual(len(data), 16)

    def test_write(self):
        data = list(range(16))
        self.assertEqual(self.spi.write(data), len(data))
