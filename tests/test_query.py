import six
import unittest
from raspi_io import Query


class TestQuery(unittest.TestCase):
    def setUp(self):
        self.query = Query('192.168.1.166')

    def test_query_info(self):
        info = self.query.get_hardware_info()
        self.assertIsInstance(info, list)
        self.assertEqual(len(info), 3)

    def test_query_device(self):
        i2c = self.query.get_i2c_list()
        self.assertLessEqual(len(i2c), 1)

        spi = self.query.get_spi_list()
        self.assertLessEqual(len(spi), 2)

    def test_query_interface(self):
        interfaces = self.query.get_iface_list()
        self.assertIsInstance(interfaces, list)
        self.assertLessEqual(len(interfaces), 2)
        self.assertIn("eth0", interfaces)

    def test_query_interface_address(self):
        for interface in self.query.get_iface_list():
            address = self.query.get_ethernet_addr(interface)
            self.assertIsInstance(address, six.string_types)
            self.assertEqual(address.count(":"), 5)


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQuery)
    unittest.TextTestRunner(verbosity=2).run(suite)

