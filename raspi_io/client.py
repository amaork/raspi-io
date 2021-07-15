# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import json
import base64
import socket
import hashlib
import websocket
from .core import RaspiBaseMsg, RaspiAckMsg, RaspiMsgDecodeError, RaspiSocketError, RaspiBinaryDataHeader, \
    DEFAULT_PORT, DATA_TRANSFER_BLOCK_SIZE, get_websocket_url
__all__ = ['RaspiWsClient', 'RaspberryManager']


class RaspiWsClient(object):
    PATH = ""

    def __init__(self, host, node, timeout=1, verbose=1):
        """RaspiWsClient

        :param host: raspberry address such as "192.168.1.100"
        :param node: node name such as "GPIO"/"I2C"
        :param timeout: timeout in seconds
        :param verbose: verbose message level
        """
        try:
            self.__error = ""
            self.__verbose = verbose
            # First using default port apply for a dynamic port
            require_address = (host, DEFAULT_PORT)
            ws = websocket.create_connection(get_websocket_url(require_address, self.PATH, node), timeout)
            ack = json.loads(ws.recv())

            # Second using first step acquired port connect server
            dynamic_address = (host, RaspiAckMsg(**ack).data)
            self._ws = websocket.create_connection(get_websocket_url(dynamic_address, self.PATH, node), timeout)
        except socket.error as err:
            raise RaspiSocketError(err)
        except (ValueError, TypeError):
            raise RaspiSocketError("Require dynamic port error")

    def _error(self, msg):
        self.__error = msg
        if self.__verbose >= 1 and msg:
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
                raise TypeError("request {!r} not {!r}".format(RaspiBaseMsg.__name__, msg.__class__.__name__))

            # Send msg
            self._ws.send(msg.dumps())
            self._output("Send:{}".format(msg))

            # Wait ack
            data = self._ws.recv()
            if not data:
                raise RuntimeError("receive ack error, no data returned")

            dict_ = json.loads(data)
            ack = RaspiAckMsg(**dict_)
            self._output("Recv:{}".format(data))

            # Check ack message
            if not ack.ack:
                self._error("{}".format(ack.data))
            return ack
        except (RuntimeError, TypeError) as err:
            self._error("{}".format(err))
            return None
        except RaspiMsgDecodeError as err:
            self._error("{}".format(err))
            return None
        except websocket.WebSocketException as err:
            self._error("{}".format(err))
            return None

    def _recv_binary_data(self, request):
        """Receive binary data

        1. send read request to server
        2. recv binary data header
        3. recv binary data piece by piece
        4. check size and md5
        5. wait ack

        :param request: read request
        :return: binary data
        """
        try:

            self._error("")
            recv_data = bytearray()

            if not isinstance(request, RaspiBaseMsg):
                raise TypeError("request {!r} not {!r}".format(RaspiBaseMsg.__name__, request.__class__.__name__))

            # First send read request
            self._ws.send(request.dumps())
            self._output("Send:{}".format(request))

            # Second receive binary data header
            data = self._ws.recv()
            if not data:
                raise RuntimeError("recv binary data header, no data returned")

            dict_ = json.loads(data)
            header = RaspiBinaryDataHeader(**dict_)
            self._output("Recv:{}".format(data))

            # Third recv binary data
            for i in range(header.slices):
                temp = self._ws.recv()
                recv_data += temp

            # Check data length and md5sum
            if len(recv_data) != header.size:
                raise ValueError("data size do not matched")

            # Check data md5 checksum
            if hashlib.md5(recv_data).hexdigest() != header.md5:
                raise ValueError("data md5 checksum do not matched")

            # Finally wait ack
            data = self._ws.recv()
            if not data:
                raise RuntimeError("receive ack error, no data returned")

            dict_ = json.loads(data)
            ack = RaspiAckMsg(**dict_)
            self._output("Recv:{}".format(data))

            # Check ack message
            if not ack.ack:
                self._error("{}".format(ack.data))

            # Return received data
            return recv_data
        except (ValueError, RuntimeError, TypeError) as err:
            self._error("{}".format(err))
            return None
        except RaspiMsgDecodeError as err:
            self._error("{}".format(err))
            return None
        except websocket.WebSocketException as err:
            self._error("{}".format(err))
            return None

    def _send_binary_data(self, header, data):
        """Send binary data to raspi io server

        1. send binary data header to server
        2. send binary data piece by piece
        3. wait ack

        :param header: binary data header
        :param data: graph data
        :return: success, return True
        """
        try:

            self._error("")

            if not isinstance(header, RaspiBinaryDataHeader):
                raise TypeError("req {!r} not {!r}".format(RaspiBinaryDataHeader.__name__, header.__class__.__name__))

            # First send binary data header
            self._ws.send(header.dumps())
            self._output("Send:{}".format(header))

            # Second send binary data using binary mode
            for i in range(header.slices):
                self._ws.send_binary(data[i * DATA_TRANSFER_BLOCK_SIZE: (i + 1) * DATA_TRANSFER_BLOCK_SIZE])

            # Wait ack
            data = self._ws.recv()
            if not data:
                raise RuntimeError("receive ack error, no data returned")

            dict_ = json.loads(data)
            ack = RaspiAckMsg(**dict_)
            self._output("Recv:{}".format(data))

            # Check ack message
            if not ack.ack:
                self._error("{}".format(ack.data))

            return ack.ack
        except (TypeError, RuntimeError) as err:
            self._error("{}".format(err))
            return None
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
