from unittest import TestCase
import telescopes
import simulation


class TestBaseTelescope(TestCase):

    def setUp(self):
        self.dut = simulation.Telescope()
        pass

    def test___init__(self):
        self.assertEqual(self.dut.device, "/dev/ttyUSB0"
        )
