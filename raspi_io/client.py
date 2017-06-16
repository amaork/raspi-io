# -*- coding: utf-8 -*-
import websocket
from .core import get_websocket_address, RaspiBasicMsg
__all__ = ['RaspiWsClient']


class RaspiWsClient(object):
    PATH = ""

    def __init__(self, host, timeout=1):
        self.__ws = websocket.create_connection(get_websocket_address(host, self.PATH), timeout)

    def send(self, msg):
        try:

            if not isinstance(msg, RaspiBasicMsg):
                print("Msg type error:{0:s}".format(type(msg)))
                return False

            self.__ws.send(msg.dumps())

        except websocket.WebSocketException as err:
            print("{}".format(err))
            return False

    def recv(self):
        try:

            return self.__ws.recv()

        except websocket.WebSocketException as err:
            print("Recv error:{}".format(err))
            return None
