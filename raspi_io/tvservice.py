# -*- coding: utf-8 -*-
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg
__all__ = ['TVService', 'TVPower', 'TVStatus', 'TVGetModes', 'TVSetExplicit']


class TVPower(RaspiBaseMsg):
    _handle = 'power_ctrl'
    _properties = {'power'}

    def __init__(self, **kwargs):
        super(TVPower, self).__init__(**kwargs)


class TVStatus(RaspiBaseMsg):
    _handle = 'get_status'

    def __init__(self, **kwargs):
        super(TVStatus, self).__init__(**kwargs)


class TVGetModes(RaspiBaseMsg):
    _handle = 'get_modes'
    _properties = {'preferred', 'group'}

    def __init__(self, **kwargs):
        kwargs.setdefault('group', "")
        kwargs.setdefault('preferred', len(kwargs.get("group")) == 0)
        super(TVGetModes, self).__init__(**kwargs)


class TVSetExplicit(RaspiBaseMsg):
    _handle = 'set_explicit'
    _properties = {'preferred', 'group', 'mode'}

    def __init__(self, **kwargs):
        kwargs.setdefault('mode', 0)
        kwargs.setdefault('group', '')
        kwargs.setdefault('preferred', len(kwargs.get("group")) == 0 and kwargs.get("mode") == 0)
        super(TVSetExplicit, self).__init__(**kwargs)


class TVService(RaspiWsClient):
    DMT = "DMT"
    CEA = "CEA"
    PATH = __name__.split(".")[-1]

    def __init__(self, host, timeout=3, verbose=1):
        """Init a tv service instance

        :param host: raspi-io server address
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        super(TVService, self).__init__(host, self.PATH, timeout, verbose)

    def get_status(self):
        """Get HDMI status

        :return: HDMI status
        """
        ret = self._transfer(TVStatus())
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else None

    def get_modes(self, group):
        """Get supported modes for GROUP (CEA, DMT)

        :return:
        """
        ret = self._transfer(TVGetModes(group=group))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else None

    def get_preferred_mode(self):
        """Get HDMI preferred settings

        :return: return HDMI preferred mode and group
        """
        ret = self._transfer(TVGetModes())
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else None

    def set_preferred_mode(self):
        """Power on HDMI with preferred settings

        :return:
        """
        ret = self._transfer(TVSetExplicit())
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def set_explicit_mode(self, group, mode):
        """Power on HDMI with explicit group and mode

        :param group: group (DMT or CEA)
        :param mode: modes get's from get_modes()
        :return: result
        """
        ret = self._transfer(TVSetExplicit(group=group, mode=mode))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def power_control(self, power):
        """Power on or off HDMI

        :param power: power
        :return: success return True, failed return False
        """
        ret = self._transfer(TVPower(power=power))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else None
