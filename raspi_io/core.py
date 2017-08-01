# -*- coding: utf-8 -*-
import json
__all__ = ['get_websocket_url', 'RaspiBaseMsg', 'RaspiAckMsg', 'RaspiMsgDecodeError', 'DEFAULT_PORT']
DEFAULT_PORT = 9876


def get_websocket_url(address, path):
    return "ws://{0:s}:{1:d}/{2:s}".format(address[0], address[1], path)


class RaspiMsgDecodeError(Exception):
    pass


class RaspiBaseMsg(object):
    _handle = ""
    _properties = set()

    def __init__(self, **kwargs):
        kwargs.setdefault('handle', self._handle)

        try:

            for key in self._properties:
                if kwargs.get(key) is None:
                    raise KeyError("do not found key:{!r}".format(key))

            self.__dict__.update(**kwargs)

        except (TypeError, KeyError, ValueError, RaspiMsgDecodeError) as e:
            raise RaspiMsgDecodeError("Decode {!r} error:{}".format(self.__class__.__name__, e))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__

    def __len__(self):
        return len(self._properties)

    def __str__(self):
        return self.dumps()

    def __iter__(self):
        for key in sorted(self.__dict__.keys()):
            yield key

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))

    def dumps(self):
        """Encode data to a dict string

        :return:
        """
        return json.dumps(self.__dict__)


class RaspiAckMsg(RaspiBaseMsg):
    _properties = {'ack', 'data'}

    def __init__(self, **kwargs):
        super(RaspiAckMsg, self).__init__(**kwargs)
