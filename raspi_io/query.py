# -*- coding: utf-8 -*-
from .version import version
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg
__all__ = ['Query', 'QueryDevice', 'QueryHardware', 'QueryVersion']


class QueryHardware(RaspiBaseMsg):
    HARDWARE = 0
    ETHERNET = 1
    _handle = 'query_hardware'
    _properties = {'query', 'params'}

    def __init__(self, **kwargs):
        kwargs.setdefault('params', "")
        super(QueryHardware, self).__init__(**kwargs)


class QueryDevice(RaspiBaseMsg):
    I2C = 0
    SPI = 1
    ETH = 2
    SERIAL = 3
    FILTER = 4
    _handle = 'query_device'
    _properties = {'query', 'filter', 'option'}

    def __init__(self, **kwargs):
        kwargs.setdefault('option', "")
        kwargs.setdefault('filter', "")
        super(QueryDevice, self).__init__(**kwargs)


class QueryVersion(RaspiBaseMsg):
    _handle = 'query_version'
    _properties = {'server', 'client'}

    def __init__(self, **kwargs):
        kwargs.setdefault('server', '')
        kwargs.setdefault('client', version)
        super(QueryVersion, self).__init__(**kwargs)


class Query(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, timeout=1, verbose=1):
        super(Query, self).__init__(host, self.PATH, timeout, verbose)

    def basic_query(self, query):
        ret = self._transfer(query)
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else None

    def get_version(self):
        return self.basic_query(QueryVersion())

    def get_hardware_info(self):
        """Query raspi hardware info

        :return:success return (hardware, revision, serial)
        """
        return self.basic_query(QueryHardware(query=QueryHardware.HARDWARE))

    def get_ethernet_addr(self, iface):
        """Get ethernet interface hardware address

        :param iface: interface name
        :return: None or ethernet interface address
        """
        return self.basic_query(QueryHardware(query=QueryHardware.ETHERNET, params=iface))

    def get_iface_list(self):
        """Get ethernet interface list

        :return: ethernet interface list
        """
        return self.basic_query(QueryDevice(query=QueryDevice.ETH))

    def get_i2c_list(self):
        """Get i2c device list

        :return: None or device name list
        """
        return self.basic_query(QueryDevice(query=QueryDevice.I2C))

    def get_spi_list(self):
        """Get spi device list

        :return: None or spi device name list
        """
        return self.basic_query(QueryDevice(query=QueryDevice.SPI))

    def get_serial_list(self, include_links=False):
        """Get serial port list

        :return: None or serial device name list
        """
        return self.basic_query(QueryDevice(query=QueryDevice.SERIAL, option=include_links))

    def get_device_list(self, query_filter):
        """Query self define query

        :param query_filter: query filter will pass to ls /dev | grep query_filter
        :return: query data
        """
        return self.basic_query(QueryDevice(query=QueryDevice.FILTER, filter=query_filter))
