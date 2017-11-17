# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import json
import base64
import socket
import websocket
from .core import get_websocket_url, RaspiBaseMsg, RaspiAckMsg, RaspiMsgDecodeError, RaspiSocketError, DEFAULT_PORT
__all__ = ['RaspiWsClient', 'RaspberryManager']


class RaspiWsClient(object):
    PATH = ""

    def __init__(self, host, node, timeout=1, verbose=1):
        try:

            self.__error = ""
            self.__verbose = verbose
            # First using default port apply for a dynamic port
            require_addr = (host, DEFAULT_PORT)
            ack = json.loads(websocket.create_connection(get_websocket_url(require_addr, self.PATH, node)).recv())

            # Second using first step acquired port connect server
            dynamic_addr = (host, RaspiAckMsg(**ack).data)
            self._ws = websocket.create_connection(get_websocket_url(dynamic_addr, self.PATH, node), timeout)
        except socket.error as err:
            raise RaspiSocketError(err)
        except (json.JSONDecodeError, TypeError):
            raise RaspiSocketError("Require dynamic port error")

    def _error(self, msg):
        self.__error = msg
        if self.__verbose >= 1:
            print(self.__error)

    def _output(self, msg):
        if self.__verbose >= 2:
            print(msg)

    @staticmethod
    def encode_binary(data):
        """Encode data to send binary data

        :param data: data to encode
        :return: after encode data
        """
        try:
            return str(base64.b64encode(data))
        except TypeError:
            return str(base64.b64encode(bytes(data) if sys.version_info.major >= 3 else "".join(map(chr, data))))

    @staticmethod
    def decode_binary(data):
        """Decode received binary data

        :param data: data to decode
        :return: after decode data for python2 is str, python3 is bytes
        """
        return base64.b64decode(data[2:-1])

    @staticmethod
    def print_binary(data, base=16):
        process = int if sys.version_info.major >= 3 else ord
        if base == 10:
            fmt = "{0:d}"
        elif base == 16:
            fmt = "0x{0:02x}"
        elif base == 8:
            fmt = "O{0:03o}"
        elif base == 2:
            fmt = "0b{0:08b}"
        else:
            fmt = "{}"

        print("[", end="")
        for i in data:
            print(fmt.format(process(i)), end=", ")
        print("\b\b]")

    def get_error(self):
        error = self.__error
        self.__error = ""
        return error

    def _transfer(self, msg):
        """Basic transfer, send a msg and get an ack

        :param msg: request message
        :return: None or RaspiAckMsg
        """
        try:

            self.__error = ""

            if not isinstance(msg, RaspiBaseMsg):
                self._error("Msg type error:{0:s}".format(type(msg)))
                return None

            # Send msg
            self._ws.send(msg.dumps())
            self._output("Send:{}".format(msg))

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


class RaspberryManager(object):
    def __init__(self, host):
        """Raspberry io manager

        :param host: raspberry pi host
        """
        self.__host = host

    def create(self, cls, *args, **kwargs):
        if not issubclass(cls, RaspiWsClient):
            raise TypeError("cls need a {!r}, not {!r}".format(RaspiWsClient.__class__, cls.__class__))

        return cls(self.__host, *args, **kwargs)
