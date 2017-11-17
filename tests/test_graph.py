# -*- coding: utf-8 -*-
import os
import time
import unittest
from raspi_io import TVService, MmalGraph


class TestMmalGraph(unittest.TestCase):
    def setUp(self):
        self.host = "192.168.1.166"
        self.tv = TVService(self.host)
        self.images = [os.path.join(os.path.dirname(__file__),  f) for f in ("cross.png", "superwoman.jpg")]

    def test_open(self):
        graph = MmalGraph(self.host)
        self.assertEqual(graph.open("1213"), False)
        self.assertEqual(graph.is_open, False)
        self.assertEqual(graph.uri, "")
        self.assertEqual(graph.display_num, MmalGraph.HDMI)

    def test_lcd(self):
        graph = MmalGraph(self.host, MmalGraph.LCD)
        self.assertEqual(graph.display_num, MmalGraph.LCD)
        for image in self.images:
            self.assertEqual(graph.open(image), True)
            self.assertEqual(graph.is_open, True)
            self.assertEqual(graph.uri, image)
            time.sleep(1)

    def test_hdmi(self):
        self.tv.set_preferred()
        time.sleep(3)
        graph = MmalGraph(self.host, MmalGraph.HDMI)
        self.assertEqual(graph.display_num, MmalGraph.HDMI)
        for image in self.images:
            self.assertEqual(graph.open(image), True)
            self.assertEqual(graph.is_open, True)
            self.assertEqual(graph.uri, image)
            time.sleep(1)
