# -*- coding: utf-8 -*-
import json
__all__ = ['get_websocket_url', 'RaspiBasicMsg']


def get_websocket_url(address, path):
    return "ws://{0:s}:{1:d}/{2:s}".format(address[0], address[1], path)


class RaspiBasicMsg(object):
    _handle = ""
    _properties = ()

    def __init__(self, **kwargs):
        kwargs.setdefault('handle', self._handle)
        self.__dict__.update(**kwargs)

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

    def loads(self, data):
        """Decode data

        :param data: encoded data, should be a str
        :return: success return object or NONE
        """
        if not isinstance(data, str):
            return None

        try:

            dict_ = json.loads(data)
            if not isinstance(dict_, dict):
                return None

            for key in self._properties:
                if dict_.get(key) is None:
                    print("{0:s} Unknown key:{1:s}".format(self.__class__.__name__, key))
                    return None

            return self.__class__(**dict_)

        except ValueError as e:
            print("Decode object '{0}' has error:{1}".format(type(self), e))
            return None

    def dumps(self):
        """Encode data to a dict string

        :return:
        """
        return json.dumps(self.__dict__)
