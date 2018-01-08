# -*- coding: utf-8 -*-
import os
from PIL import Image
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg, get_binary_data_header
__all__ = ['MmalGraph', 'GraphInit', 'GraphClose', 'GraphProperty']


class GraphInit(RaspiBaseMsg):
    _handle = 'init'
    _properties = {'display_num'}

    def __init__(self, **kwargs):
        super(GraphInit, self).__init__(**kwargs)


class GraphClose(RaspiBaseMsg):
    _handle = 'close'

    def __init__(self, **kwargs):
        super(GraphClose, self).__init__(**kwargs)


class GraphProperty(RaspiBaseMsg):
    _handle = 'get_property'
    _properties = {'property'}
    URI, IS_OPEN, DISPLAY_NUM = 1, 2, 3

    def __init__(self, **kwargs):
        super(GraphProperty, self).__init__(**kwargs)


class MmalGraph(RaspiWsClient):
    LCD = 4
    HDMI = 5
    REDUCE_SIZE_FORMAT = ("BMP",)
    PATH = __name__.split(".")[-1]

    def __init__(self, host, display_num=HDMI, reduce_size=True, timeout=3, verbose=1):
        """Display a graph on raspberry pi specified monitor

        :param host: raspberry pi address
        :param display_num: display monitor number (HDMI or LCD)
        :param reduce_size: reduce bmp graph size then transfer
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        super(MmalGraph, self).__init__(host, str(display_num), timeout, verbose)
        ret = self._transfer(GraphInit(display_num=display_num))
        if not isinstance(ret, RaspiAckMsg) or not ret.ack:
            raise RuntimeError(ret.data)

        self.__uri = ""
        self.__reduce_size = reduce_size

    def __del__(self):
        try:
            self.close()
        except AttributeError:
            pass

    @property
    def uri(self):
        return self.__uri

    @property
    def is_open(self):
        ret = self._transfer(GraphProperty(property=GraphProperty.IS_OPEN))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else False

    @property
    def display_num(self):
        ret = self._transfer(GraphProperty(property=GraphProperty.DISPLAY_NUM))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else None

    def open(self, path, reduce_size=None):
        """Open an image display on raspberry pi via mmal video core

        :param path:
        :param reduce_size: reduce bmp graph size then transfer
        :return:
        """
        self.__uri = ""
        png_path = "{}.png".format(os.path.basename(path))
        reduce_size = reduce_size if reduce_size is not None else self.__reduce_size

        try:
            # Open original file
            image = Image.open(path)
            fmt = image.format

            # Reduce image size to png format
            if reduce_size and fmt in self.REDUCE_SIZE_FORMAT:
                image.save(png_path)
                path = png_path
                fmt = "PNG"

            # Read data to memory
            with open(path, "rb") as fp:
                data = fp.read()

            # First transfer header info
            ret = self._send_binary_data(get_binary_data_header(data, fmt, "open"), data)
            if isinstance(ret, RaspiAckMsg) and ret.ack:
                self.__uri = path
                return ret.data
            else:
                return False
        except IOError as err:
            self._error("Open error:{}".format(err))
            return False
        finally:
            if os.path.isfile(png_path):
                os.remove(png_path)

    def close(self):
        ret = self._transfer(GraphClose())
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else False
