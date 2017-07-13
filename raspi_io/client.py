# -*- coding: utf-8 -*-
import json
import websocket
from .core import get_websocket_url, RaspiBaseMsg, RaspiAckMsg, RaspiMsgDecodeError
__all__ = ['RaspiWsClient']


class RaspiWsClient(object):
    PATH = ""

    def __init__(self, address, timeout=1, verbose=1):
        self.__error = ""
        self.__verbose = verbose
        self.__ws = websocket.create_connection(get_websocket_url(address, self.PATH), timeout)

    def _error(self, msg):
        self.__error = msg
        if self.__verbose >= 1:
            print(self.__error)

    def _output(self, msg):
        if self.__verbose >= 2:
            print(msg)

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
            self.__ws.send(msg.dumps())
            self._output("Send:{}".format(msg))

            # Wait ack
            data = self.__ws.recv()
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
