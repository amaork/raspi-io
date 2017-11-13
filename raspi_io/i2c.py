# -*- coding: utf-8 -*-
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg
__all__ = ['I2C', 'I2CDevice' 'I2CRead', 'I2CWrite']


class I2CRead(RaspiBaseMsg):
    READ, IOCTL = 0, 1
    _handle = 'read'
    _properties = {'addr', 'size', 'type'}

    def __init__(self, **kwargs):
        kwargs.setdefault('type', self.READ)
        super(I2CRead, self).__init__(**kwargs)

    def is_ioctl_read(self):
        return self.type == self.IOCTL


class I2CWrite(RaspiBaseMsg):
    WRITE, IOCTL = 0, 1
    _handle = 'write'
    _properties = {'addr', 'data', 'type'}

    def __init__(self, **kwargs):
        kwargs.setdefault('type', self.WRITE)
        super(I2CWrite, self).__init__(**kwargs)

    def is_ioctl_write(self):
        return self.type == self.IOCTL


class I2CDevice(RaspiBaseMsg):
    _handle = 'open'
    _properties = {'bus', 'addr', 'flags', 'delay', 'tenbit', 'iaddr_bytes', 'page_bytes'}

    def __init__(self, **kwargs):
        super(I2CDevice, self).__init__(**kwargs)


class I2C(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, bus, device_address, tenbit=0, flags=0, delay=5, iaddr_bytes=1, page_bytes=8,
                 timeout=1, verbose=1):
        """Init a i2c instance

        :param host: raspi-io server address
        :param bus: i2c bus name
        :param device_address: i2c device address not internal address
        :param tenbit: if set i2c device address is tenbit
        :param flags: i2c flags
        :param delay: i2c internal operate delay, unit millisecond
        :param iaddr_bytes: i2c internal address bytes
        :param page_bytes: i2c max number of bytes per page
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        super(I2C, self).__init__(host, bus, timeout, verbose)
        ret = self._transfer(I2CDevice(bus=bus, addr=device_address,
                                       tenbit=tenbit, flags=flags, delay=delay,
                                       iaddr_bytes=iaddr_bytes, page_bytes=page_bytes))

        if not isinstance(ret, RaspiAckMsg) or not ret.ack:
            raise RuntimeError(ret.data)

    def read(self, address, size):
        """Read data from i2c

        :param address: i2c device internal address
        :param size: read size(bytes)
        :return: success return read data(bytes) else ""
        """
        ret = self._transfer(I2CRead(addr=address, size=size))
        return self.decode_binary(ret.data) if isinstance(ret, RaspiAckMsg) and ret.ack else ""

    def write(self, address, data):
        """Write data to specific address

        :param address: i2c internal address
        :param data: data to write(Python2,3 both can using ctypes, python3 using bytes)
        :return: success return write data size else -1
        """
        ret = self._transfer(I2CWrite(addr=address, data=self.encode_binary(data)))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else -1

    def ioctl_read(self, address, size):
        """Using ioctl read data from i2c

        :param address: i2c device internal address
        :param size: read size(bytes)
        :return: success return read data size else -1
        """
        ret = self._transfer(I2CRead(addr=address, size=size, type=I2CRead.IOCTL))
        return self.decode_binary(ret.data) if isinstance(ret, RaspiAckMsg) and ret.ack else ""

    def ioctl_write(self, address, data):
        """Using ioctl write data to specific address

        :param address: i2c internal address
        :param data: data to write
        :return: success return write data size else -1
        """
        ret = self._transfer(I2CWrite(addr=address, data=self.encode_binary(data), type=I2CWrite.IOCTL))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else -1
