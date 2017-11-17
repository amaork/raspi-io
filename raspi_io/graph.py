# -*- coding: utf-8 -*-
import os
import json
import hashlib
import websocket
from PIL import Image
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg, RaspiMsgDecodeError
__all__ = ['MmalGraph', 'GraphInit', 'GraphClose', 'GraphHeader', 'GraphProperty']


class GraphInit(RaspiBaseMsg):
    _handle = 'init'
    _properties = {'display_num'}

    def __init__(self, **kwargs):
        super(GraphInit, self).__init__(**kwargs)


class GraphClose(RaspiBaseMsg):
    _handle = 'close'

    def __init__(self, **kwargs):
        super(GraphClose, self).__init__(**kwargs)


class GraphHeader(RaspiBaseMsg):
    _handle = 'open'
    _properties = {'size', 'md5', 'slices', 'format'}

    def __init__(self, **kwargs):
        super(GraphHeader, self).__init__(**kwargs)


class GraphProperty(RaspiBaseMsg):
    _handle = 'get_property'
    _properties = {'property'}
    URI, IS_OPEN, DISPLAY_NUM = 1, 2, 3

    def __init__(self, **kwargs):
        super(GraphProperty, self).__init__(**kwargs)


class MmalGraph(RaspiWsClient):
    LCD = 4
    HDMI = 5
    BLOCK_SIZE = 512 * 1024
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

    @staticmethod
    def calc_slice_size(total, block):
        if total <= block:
            return 1
        elif total % block == 0:
            return total // block
        else:
            return total // block + 1

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

            # Get header info
            size = len(data)
            md5 = hashlib.md5(data).hexdigest()
            slices = self.calc_slice_size(size, self.BLOCK_SIZE)

            # First transfer header info
            ret = self.__transfer_graph(GraphHeader(size=size, md5=md5, format=fmt, slices=slices), data)
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

    def __transfer_graph(self, header, data):
        """Transfer graph to raspberry

        :param header: graph header
        :param data: graph data
        :return: success, return True
        """
        try:

            self._error("")

            if not isinstance(header, RaspiBaseMsg):
                self._error("Msg type error, not:{!r}".format(header.__class__.__name__))
                return None

            # First send graph header
            self._ws.send(header.dumps())
            self._output("Send:{}".format(header))

            # Second send graph data using binary mode
            for i in range(header.slices):
                self._ws.send_binary(data[i * self.BLOCK_SIZE: (i + 1) * self.BLOCK_SIZE])

            # Wait ack
            data = self._ws.recv()
            self._output("Recv:{}".format(data))
            if not data:
                self._error("Receive ack error, no data returned")
                return None

            dict_ = json.loads(data)
            ack = RaspiAckMsg(**dict_)

            # Check ack message
            if not ack.ack:
                self._error("{}".format(ack.data))

            return ack

        except RaspiMsgDecodeError as err:
            self._error("{}".format(err))
            return None
        except websocket.WebSocketException as err:
            self._error("{}".format(err))
            return None
