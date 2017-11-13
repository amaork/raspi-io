# -*- coding: utf-8 -*-
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg
__all__ = ['SPIOpen', 'SPIClose', 'SPIRead', 'SPIWrite', 'SPIXfer', 'SPIXfer2', 'SPI']


class SPIOpen(RaspiBaseMsg):
    _handle = 'open'
    _properties = {'device', 'max_speed', 'cshigh', 'no_cs', 'loop', 'lsbfirst', 'mode', 'threewire'}

    def __init__(self, **kwargs):
        super(SPIOpen, self).__init__(**kwargs)


class SPIClose(RaspiBaseMsg):
    _handle = 'close'
    _properties = {'device'}

    def __init__(self, **kwargs):
        super(SPIClose, self).__init__(**kwargs)


class SPIRead(RaspiBaseMsg):
    _handle = 'read'
    _properties = {'size'}

    def __init__(self, **kwargs):
        super(SPIRead, self).__init__(**kwargs)


class SPIWrite(RaspiBaseMsg):
    _handle = 'write'
    _properties = {'data'}

    def __init__(self, **kwargs):
        super(SPIWrite, self).__init__(**kwargs)


class SPIXfer(RaspiBaseMsg):
    _handle = 'xfer'
    _properties = {'write_data', 'read_size', 'speed', 'delay'}

    def __init__(self, **kwargs):
        super(SPIXfer, self).__init__(**kwargs)


class SPIXfer2(SPIXfer):
    _handle = 'xfer2'

    def __init__(self, **kwargs):
        super(SPIXfer2, self).__init__(**kwargs)


class SPI(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, device, max_speed=50,
                 mode=0, cshigh=False, no_cs=False, loop=False, lsbfirst=False, threewire=False, timeout=1, verbose=1):
        """

        :param host: raspi-io server address
        :param device: spi device name, such as /dev/spidev0.0
        :param max_speed: spi max speed unit khz, 8000 = 8Mhz
        :param mode: SPI mode as two bit pattern of clock polarity and phase [CPOL|CPHA], min: 0b00 = 0, max: 0b11 = 3
        :param cshigh:
        :param no_cs: Set the "SPI_NO_CS" flag to disable use of the chip select (although the driver may still own the CS pin)
        :param loop: Set the "SPI_LOOP" flag to enable loopback mode
        :param lsbfirst: LSB first
        :param threewire: SI/SO signals shared
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        super(SPI, self).__init__(host, device, timeout, verbose)
        self.__opened = False
        self.__device = device
        ret = self._transfer(SPIOpen(device=device, max_speed=max_speed, mode=mode, cshigh=cshigh,
                                     no_cs=no_cs, loop=loop, lsbfirst=lsbfirst, threewire=threewire))

        self.__opened = ret.ack if isinstance(ret, RaspiAckMsg) else False
        if not self.__opened:
            raise RuntimeError(ret.data)

    def __del__(self):
        try:
            if self.__opened:
                self._transfer(SPIClose(device=self.__device))
        except AttributeError:
            pass

    def read(self, size):
        """Read specify bytes data from spi

        :param size: read size
        :return: data
        """
        ret = self._transfer(SPIRead(size=size))
        return self.decode_binary(ret.data) if isinstance(ret, RaspiAckMsg) and ret.ack else ""

    def write(self, data):
        """Write data to spi

        :param data: data to write
        :return: write data size
        """
        ret = self._transfer(SPIWrite(data=self.encode_binary(data)))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else -1

    def xfer(self, write_data, read_size, speed=0, delay=0):
        """Performs an SPI transaction. Chip-select should be released and reactivated between blocks

        :param write_data: data will write to spi
        :param read_size: data will read from spi
        :param speed: speed
        :param delay: specifies the delay in usec between blocks.
        :return: read data
        """
        ret = self._transfer(SPIXfer(write_data=self.encode_binary(write_data),
                             read_size=read_size, speed=speed, delay=delay))
        return self.decode_binary(ret.data) if isinstance(ret, RaspiAckMsg) and ret.ack else ""

    def xfer2(self, write_data, read_size, speed=0, delay=0):
        """Performs an SPI transaction. Chip-select should be held active between blocks.

        :param write_data: data will write to spi
        :param read_size: data will read from spi
        :param speed: speed
        :param delay: specifies the delay in usec between blocks.
        :return: read data
        """
        ret = self._transfer(SPIXfer2(write_data=self.encode_binary(write_data),
                                      read_size=read_size, speed=speed, delay=delay))
        return self.decode_binary(ret.data) if isinstance(ret, RaspiAckMsg) and ret.ack else ""
