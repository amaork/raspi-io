# -*- coding: utf-8 -*-
import hashlib
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg, get_binary_data_header
__all__ = ['SPIFlashInstruction', 'SPIFlashDevice', 'SPIFlashClose',
           'SPIFlashProbe', 'SPIFlashErase', 'SPIFlashReadChip',
           'SPIFlashReadStatus', 'SPIFlashWriteStatus', 'SPIFlash']


class SPIFlashInstruction(RaspiBaseMsg):
    _properties = {'read_id', 'read_sr', 'write_sr', 'read_sr1', 'read_sr2',
                   'chip_erase', 'page_read', 'page_write', 'write_enable', 'write_disable'}

    def __init__(self, **kwargs):
        # Read identification
        kwargs.setdefault('read_id', 0x9f)
        # Read status register
        kwargs.setdefault('read_sr', 0x05)
        kwargs.setdefault('write_sr', 0x1)
        kwargs.setdefault('read_sr1', 0x5)
        kwargs.setdefault('read_sr2', 0x35)

        kwargs.setdefault('chip_erase', 0x60)
        kwargs.setdefault('page_read', 0x03)
        kwargs.setdefault('page_write', 0x2)
        kwargs.setdefault('write_enable', 0x6)
        kwargs.setdefault('write_disable', 0x4)
        super(SPIFlashInstruction, self).__init__(**kwargs)


class SPIFlashDevice(RaspiBaseMsg):
    _handle = 'open'
    _properties = {'device', 'speed', 'page_size', 'chip_size', 'instruction', 'cpol', 'cpha'}

    def __init__(self, **kwargs):
        super(SPIFlashDevice, self).__init__(**kwargs)


class SPIFlashProbe(RaspiBaseMsg):
    _handle = 'probe'

    def __init__(self, **kwargs):
        super(SPIFlashProbe, self).__init__(**kwargs)


class SPIFlashErase(RaspiBaseMsg):
    _handle = 'erase'

    def __init__(self, **kwargs):
        super(SPIFlashErase, self).__init__(**kwargs)


class SPIFlashClose(RaspiBaseMsg):
    _handle = 'close'

    def __init__(self, **kwargs):
        super(SPIFlashClose, self).__init__(**kwargs)


class SPIFlashReadChip(RaspiBaseMsg):
    _handle = 'read_chip'

    def __init__(self, **kwargs):
        super(SPIFlashReadChip, self).__init__(**kwargs)


class SPIFlashReadStatus(RaspiBaseMsg):
    _handle = 'read_status'

    def __init__(self, **kwargs):
        super(SPIFlashReadStatus, self).__init__(**kwargs)


class SPIFlashWriteStatus(RaspiBaseMsg):
    _handle = 'write_status'
    _properties = {'status'}

    def __init__(self, **kwargs):
        super(SPIFlashWriteStatus, self).__init__(**kwargs)


class SPIFlash(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, device, speed, page_size, chip_size,
                 cpol=False, cpha=False, instruction=None, timeout=30, verbose=1):
        """

        :param host: raspi-io server address
        :param device: spi device name, such as /dev/spidev0.0
        :param speed: spi bus speed
        :param page_size: spi flash page size (unit byte)
        :param chip_size: spi flash chip size (unit byte)
        :param cpol: spi clock polarity , clk idle state (False clk idle --> Low, True clk idle --> High)
        :param cpha: spi clock phase, strobe edge (False first edge, True second edge)
        :param instruction: spi flash instruction
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        cpol = True if cpol else False
        cpha = True if cpha else False
        super(SPIFlash, self).__init__(host, device, timeout, verbose)
        flash_instruction = instruction if isinstance(instruction, SPIFlashInstruction) else SPIFlashInstruction()
        ret = self._transfer(SPIFlashDevice(device=device, speed=speed, cpol=cpol, cpha=cpha,
                                            page_size=page_size, chip_size=chip_size,
                                            instruction=flash_instruction.dict))
        if not isinstance(ret, RaspiAckMsg) or not ret.ack:
            raise RuntimeError(ret.data)

    def __del__(self):
        try:
            self._transfer(SPIFlashClose())
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

    def read_status(self):
        """Get spi flash status

        :return: flash status register value
        """
        ret = self._transfer(SPIFlashReadStatus())
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else 0xffff

    def write_status(self, status):
        """Write spi flash status

        :return: success return true, failed return false
        """
        ret = self._transfer(SPIFlashWriteStatus(status=status))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def read_chip(self):
        """Read whole spi flash chip

        :return: flash data
        """
        return self._recv_binary_data(SPIFlashReadChip())

    def write_chip(self, data, verify=False):
        """Write data to chip

        :param data: spi data
        :param verify: verify data after write
        :return: write result
        """
        # First erase chip
        if not self.erase():
            self._error("Erase chip error:{}".format(self.get_error()))
            return False
        # Second write data to chip
        if not self.send_binary_data(get_binary_data_header(data, handle="write_chip"), data):
            self._error("Write chip error:{}".format(self.get_error()))
            return False

        # Finally verify
        if verify and hashlib.md5(self.read_chip()).hexdigest() != hashlib.md5(data).hexdigest():
            self._error("Verify error, md5 do not matched")
            return False

        return True
