# -*- coding: utf-8 -*-
import uuid
import hashlib
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg, get_binary_data_header
from .spi_flash import SPIFlashInstruction, SPIFlashErase, SPIFlashClose, \
    SPIFlashProbe, SPIFlashReadChip, SPIFlashReadStatus, SPIFlashWriteStatus


class GPIOSPIFlashDevice(RaspiBaseMsg):
    _handle = 'open'
    _properties = {'clk', 'cs', 'mosi', 'miso', 'page_size', 'chip_size', 'instruction'}

    def __init__(self, **kwargs):
        super(GPIOSPIFlashDevice, self).__init__(**kwargs)


class GPIOSPIFlash(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, page_size, chip_size,
                 cs=8, clk=11, mosi=10, miso=9, instruction=None, timeout=200, verbose=1):
        """

        :param host: raspi-io server address
        :param page_size: spi flash page size (unit byte)
        :param chip_size: spi flash chip size (unit byte)
        :param cs: spi chip select gpio pin
        :param clk: spi clk gpio pin
        :param mosi: spi mosi gpio pin
        :param miso: spi miso gpio pin
        :param instruction: spi flash instruction
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        device_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, '{}:{}:{}:{}'.format(cs, clk, mosi, miso)))
        super(GPIOSPIFlash, self).__init__(host, device_uuid, timeout, verbose)
        flash_instruction = instruction if isinstance(instruction, SPIFlashInstruction) else SPIFlashInstruction()
        ret = self._transfer(GPIOSPIFlashDevice(cs=cs, clk=clk, mosi=mosi, miso=miso,
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
        if not self._send_binary_data(get_binary_data_header(data, handle="write_chip"), data):
            self._error("Write chip error:{}".format(self.get_error()))
            return False

        # Finally verify
        if verify and hashlib.md5(self.read_chip()).hexdigest() != hashlib.md5(data).hexdigest():
            self._error("Verify error, md5 do not matched")
            return False

        return True
