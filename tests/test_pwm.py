import unittest
from raspi_io import SoftPWM, GPIO


class TestSoftPWM(unittest.TestCase):
    def setUp(self):
        self.pwm = SoftPWM(('192.168.1.166', 9876), GPIO.BCM, 21, 1000, verbose=0)

    def tearDown(self):
        del self.pwm

    def test_start(self):
        self.assertEqual(self.pwm.start(101), False)
        self.assertEqual(self.pwm.is_running(), False)
        self.assertEqual(self.pwm.start(-1), False)
        self.assertEqual(self.pwm.is_running(), False)
        self.assertEqual(self.pwm.start(0), True)
        self.assertEqual(self.pwm.is_running(), True)
        self.assertEqual(self.pwm.start(100), True)
        self.assertEqual(self.pwm.is_running(), True)

    def test_stop(self):
        self.assertEqual(self.pwm.stop(), True)
        self.assertEqual(self.pwm.is_running(), False)


if __name__ == "__main__":
    unittest.main()
