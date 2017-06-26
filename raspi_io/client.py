# -*- coding: utf-8 -*-
import websocket
from .core import get_websocket_url, RaspiBasicMsg, RaspiAckMsg
__all__ = ['RaspiWsClient']


class RaspiWsClient(object):
    PATH = ""

    def __init__(self, address, timeout=1):
        self.__ws = websocket.create_connection(get_websocket_url(address, self.PATH), timeout)

    def _transfer(self, msg):
        """Basic transfer, send a msg and get an ack

        :param msg: request message
        :return: None or RaspiAckMsg
        """
        try:

            if not isinstance(msg, RaspiBasicMsg):
                print("Msg type error:{0:s}".format(type(msg)))
                return None

            # Send msg
            self.__ws.send(msg.dumps())

            # Wait ack msg
            data = self.__ws.recv()
            ack = RaspiAckMsg().loads(data)
            if not isinstance(ack, RaspiAckMsg):
                print("Parse ack message error!")
                return None

            # Check ack message
            if not ack.ack:
                print("{}".format(ack.data))

            return ack

        except websocket.WebSocketException as err:
            print("{}".format(err))
            return None
