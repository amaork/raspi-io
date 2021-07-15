# -*- coding: utf-8 -*-
import json
import hashlib
__all__ = ['get_websocket_url', 'get_binary_data_header',
           'RaspiBaseMsg', 'RaspiAckMsg', 'RaspiBinaryDataHeader',
           'RaspiMsgDecodeError', 'RaspiSocketError', 'DEFAULT_PORT', 'DATA_TRANSFER_BLOCK_SIZE']
DEFAULT_PORT = 9876
DATA_TRANSFER_BLOCK_SIZE = 512 * 1024


def get_websocket_url(address, path, node):
    return "ws://{0:s}:{1:d}/{2:s}?{3:s}".format(address[0], address[1], path, node)


def get_binary_data_header(data, fmt="bin", handle=""):
    """Get binary data transfer info

    :param data: binary data
    :param fmt: data format
    :param handle: which function process this data
    :return: data size, data md5, data block slices
    """
    size = len(data)
    block = DATA_TRANSFER_BLOCK_SIZE
    md5 = hashlib.md5(data).hexdigest()

    if size <= block:
        slices = 1
    elif size % block == 0:
        slices = size // block
    else:
        slices = size // block + 1

    return RaspiBinaryDataHeader(size=size, md5=md5, slices=slices, format=fmt, handle=handle)


class RaspiMsgDecodeError(Exception):
    pass


class RaspiSocketError(Exception):
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

    @property
    def dict(self):
        return self.__dict__.copy()

    def dumps(self):
        """Encode data to a dict string

        :return:
        """
        return json.dumps(self.__dict__)


class RaspiAckMsg(RaspiBaseMsg):
    _properties = {'ack', 'data'}

    def __init__(self, **kwargs):
        super(RaspiAckMsg, self).__init__(**kwargs)


class RaspiBinaryDataHeader(RaspiBaseMsg):
    _properties = {'size', 'md5', 'slices', 'format'}

    def __init__(self, **kwargs):
        super(RaspiBinaryDataHeader, self).__init__(**kwargs)
