# -*- coding: utf-8 -*-
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg, get_binary_data_header
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


class SPIFlashOpen(RaspiBaseMsg):
    _handle = 'open'
    _properties = {'device', 'speed', 'page_size', 'chip_size',
                   'read_id', 'read_sr', 'chip_erase', 'page_read', 'page_write', 'write_enable', 'write_disable'}

    def __init__(self, **kwargs):
        # Read identification
        kwargs.setdefault('read_id', 0x9f)
        # Read status register
        kwargs.setdefault('read_sr', 0x05)
        kwargs.setdefault('chip_erase', 0x60)
        kwargs.setdefault('page_read', 0x03)
        kwargs.setdefault('page_write', 0x2)
        kwargs.setdefault('write_enable', 0x6)
        kwargs.setdefault('write_disable', 0x4)
        super(SPIFlashOpen, self).__init__(**kwargs)


class SPIFlashProbe(RaspiBaseMsg):
    _handle = 'probe'

    def __init__(self, **kwargs):
        super(SPIFlashProbe, self).__init__(**kwargs)


class SPIFlashErase(RaspiBaseMsg):
    _handle = 'erase'

    def __init__(self, **kwargs):
        super(SPIFlashErase, self).__init__(**kwargs)


class SPIFlashDataHeader(RaspiBaseMsg):
    _properties = {'size', 'md5', 'slices', 'read'}

    def __init__(self, **kwargs):
        super(SPIFlashDataHeader, self).__init__(**kwargs)


class SPIFlashReadChip(RaspiBaseMsg):
    _handle = 'read_chip'

    def __init__(self, **kwargs):
        super(SPIFlashReadChip, self).__init__(**kwargs)


class SPIFlashWriteChip(RaspiBaseMsg):
    _handle = 'write_chip'
    _properties = {'size', 'md5', 'slices'}

    def __init__(self, **kwargs):
        super(SPIFlashWriteChip, self).__init__(**kwargs)


class SPIFlash(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, device, speed, page_size, chip_size, instruction=None, timeout=30, verbose=1):
        """

        :param host: raspi-io server address
        :param device: spi device name, such as /dev/spidev0.0
        :param speed: spi bus speed
        :param page_size: spi flash page size (unit byte)
        :param chip_size: spi flash chip size (unit byte)
        :param instruction: spi flash instruction dict
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        super(SPIFlash, self).__init__(host, device, timeout, verbose)
        self.__speed = speed
        self.__device = SPIFlashOpen(device=device, speed=speed, page_size=page_size, chip_size=chip_size)
        # Flash instruction set
        if isinstance(instruction, dict):
            self.__device.read_id = instruction.get("read_id") or self.__device.read_id
            self.__device.read_sr = instruction.get("read_sr") or self.__device.read_sr
            self.__device.chip_erase = instruction.get("chip_erase") or self.__device.chip_erase
            self.__device.page_read = instruction.get("page_read") or self.__device.page_read
            self.__device.page_write = instruction.get("page_write") or self.__device.page_write
            self.__device.write_enable = instruction.get("write_enable") or self.__device.write_enable
            self.__device.write_disable = instruction.get("write_disable") or self.__device.write_disable

        # Open spi flash
        ret = self._transfer(self.__device)
        self.__opened = ret.ack if isinstance(ret, RaspiAckMsg) else False
        if not self.__opened:
            raise RuntimeError(ret.data)

    def __del__(self):
        try:
            if self.__opened:
                self._transfer(SPIClose(device=self.__device))
        except AttributeError:
            pass

    def probe(self):
        """Probe spi flash

        :return: flash manufacturer id, device_id
        """
        ret = self._transfer(SPIFlashProbe())
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else (0xff, 0xffff)

    def erase(self):
        """Erase chip

        :return: result
        """
        ret = self._transfer(SPIFlashErase())
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def read_chip(self):
        """Read whole spi flash chip

        :return: flash data
        """
        # First send read chip request
        ret = self._transfer(SPIFlashReadChip())
        if not isinstance(ret, RaspiAckMsg) or not ret.ack:
            return None

        # Second read data piece by piece
        return self.__transfer_data(ret.data)

    def write_chip(self, data):
        """Write data to chip

        :param data: spi data
        :return: write result
        """
        size, md5, slices = get_binary_data_header(data)

        # First send write chip request and data info
        ret = self._transfer(SPIFlashWriteChip(size=size, md5=md5, slices=slices))


    def __transfer_data(self, header):
        pass
