# -*- coding: utf-8 -*-
import time
import unittest
from raspi_io import TVService


class TestTVService(unittest.TestCase):
    def setUp(self):
        self.tv = TVService("192.168.1.166")

    def test_power(self):
        self.tv.power_control(False)
        print("Power off")
        time.sleep(3)
        self.tv.power_control(True)
        print("Power on")

    def test_status(self):
        st = self.tv.get_status()
        self.assertIsInstance(st, dict)
        self.assertIn("res", st)
        self.assertIn("rate", st)
        self.assertIn("mode", st)
        self.assertIn("ratio", st)
        self.assertIn("group", st)
        self.assertIn("scan_mode", st)

    def test_get_modes(self):
        with self.assertRaises(TypeError):
            self.tv.get_modes()

        with self.assertRaises(TypeError):
            self.tv.get_modes(0)

        self.assertIs(self.tv.get_modes("1234"), None)

        for mode in self.tv.get_modes(TVService.DMT):
            print(mode)

        for mode in self.tv.get_modes(TVService.CEA):
            print(mode)

        print("Preferred mode:{}".format(self.tv.get_preferred_mode()))

    def test_set_modes(self):
        with self.assertRaises(TypeError):
            self.tv.set_explicit()

        self.assertEqual(self.tv.set_preferred(), True)
        self.assertEqual(self.tv.set_explicit("123", 0), False)
        self.assertEqual(self.tv.set_explicit(TVService.DMT, 46), True)


if __name__ == "__main__":
    unittest.main()
