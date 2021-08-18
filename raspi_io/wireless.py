# -*- coding: utf-8 -*-
from .core import RaspiBaseMsg
from .client import RaspiWsClient
__all__ = ['JoinNetwork', 'LeaveNetwork', 'GetNetworks', 'BackupConfigure', 'Wireless']


class GetNetworks(RaspiBaseMsg):
    _handle = 'get_networks'


class JoinNetwork(RaspiBaseMsg):
    _handle = 'join_network'
    _properties = {'ssid', 'psk', 'key_mgmt', 'priority', 'scan_ssid', 'id_str'}

    def __init__(self, **kwargs):
        kwargs.setdefault('id_str', '')
        kwargs.setdefault('priority', 0)
        kwargs.setdefault('key_mgmt', '')
        kwargs.setdefault('scan_ssid', 0)
        super(JoinNetwork, self).__init__(**kwargs)


class LeaveNetwork(RaspiBaseMsg):
    _handle = 'leave_network'
    _properties = {'ssid', 'id_str'}


class BackupConfigure(RaspiBaseMsg):
    _handle = 'backup_configure'


class Wireless(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, timeout=1, verbose=1):
        super(Wireless, self).__init__(host, self.PATH, timeout, verbose)

    def get_networks(self):
        return self.check_result(self._transfer(GetNetworks()))

    def join_network(self, **kwargs):
        return self.check_result(self._transfer(JoinNetwork(**kwargs)))

    def leave_network(self, ssid, id_str=''):
        return self.check_result(self._transfer(LeaveNetwork(ssid=ssid, id_str=id_str)))
