# -*- coding: utf-8 -*-
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg, DEFAULT_PORT
__all__ = ['RaspiWsPort', 'RaspiIOSetting', 'get_server_port']


class RaspiWsPort(RaspiBaseMsg):
    _handle = 'get_port'
    _properties = {'path', 'node'}

    def __init__(self, **kwargs):
        super(RaspiWsPort, self).__init__(**kwargs)


class RaspiIOSetting(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, address, timeout=1, verbose=1):
        super(RaspiIOSetting, self).__init__(address, timeout, verbose)

    def get_port(self, path, node):
        ret = self._transfer(RaspiWsPort(path=path, node=node))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else DEFAULT_PORT


def get_server_port(host, path, node):
    setting = RaspiIOSetting((host, DEFAULT_PORT))
    return setting.get_port(path, node)


