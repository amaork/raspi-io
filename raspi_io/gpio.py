# -*- coding: utf-8 -*-
import uuid
from .client import RaspiWsClient
from .core import RaspiBasicMsg, RaspiAckMsg
__all__ = ['GPIO', 'GPIOEvent', 'GPIOChannel', 'GPIOCtrl', 'GPIOSetup', 'GPIOMode',
           'SoftPWM', 'GPIOSoftPWM', 'GPIOSoftPWMCtrl']


class GPIOMode(RaspiBasicMsg):
    BCM = 11
    BOARD = 10
    _handle = 'setmode'
    _properties = ('mode',)

    def __init__(self, **kwargs):
        super(GPIOMode, self).__init__(**kwargs)


class GPIOCtrl(RaspiBasicMsg):
    LOW = 0
    HIGH = 1
    _handle = 'output'
    _properties = ('channel', 'value')

    def __init__(self, **kwargs):
        super(GPIOCtrl, self).__init__(**kwargs)


class GPIOEvent(RaspiBasicMsg):
    # Edge
    RISING = 31
    FALLING = 32
    BOTH = 33
    _handle = 'event'
    _properties = ('channel', 'edge', 'callback')

    def __init__(self, **kwargs):
        kwargs.setdefault('edge', None)
        kwargs.setdefault('callback', None)
        super(GPIOEvent, self).__init__(**kwargs)


class GPIOSetup(RaspiBasicMsg):
    # Direction
    IN = 1
    OUT = 0

    # Pull up down
    PUD_DOWN = 21
    PUD_OFF = 20
    PUD_UP = 22
    _handle = 'setup'
    _properties = ('channel', 'direction', 'pull_up_down', 'initial')

    def __init__(self, **kwargs):
        kwargs.setdefault('initial', GPIOCtrl.LOW)
        kwargs.setdefault('pull_up_down', GPIOSetup.PUD_OFF)
        super(GPIOSetup, self).__init__(**kwargs)


class GPIOChannel(RaspiBasicMsg):
    _handle = 'input'
    _properties = ('channel', 'value')

    def __init__(self, **kwargs):
        kwargs.setdefault('value', 0)
        super(GPIOChannel, self).__init__(**kwargs)


class GPIOSoftPWM(RaspiBasicMsg):
    _handle = 'pwm'
    _properties = ('mode', 'channel', 'frequency')

    def __init__(self, **kwargs):
        super(GPIOSoftPWM, self).__init__(**kwargs)


class GPIOSoftPWMCtrl(RaspiBasicMsg):
    _handle = 'pwm_ctrl'
    _properties = ('uuid', 'duty')

    def __init__(self, **kwargs):
        kwargs.setdefault('duty', 0)
        super(GPIOSoftPWMCtrl, self).__init__(**kwargs)


class GPIO(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    BCM = GPIOMode.BCM
    BOARD = GPIOMode.BOARD

    IN = GPIOSetup.IN
    OUT = GPIOSetup.OUT

    LOW = GPIOCtrl.LOW
    HIGH = GPIOCtrl.HIGH

    PUD_UP = GPIOSetup.PUD_UP
    PUD_OFF = GPIOSetup.PUD_OFF
    PUD_DOWN = GPIOSetup.PUD_DOWN

    def __init__(self, address, timeout=1):
        super(GPIO, self).__init__(address, timeout)

    def setmode(self, mode):
        self._transfer(GPIOMode(mode=mode))

    def input(self, channel):
        ack = self._transfer(GPIOChannel(channel=channel))
        if not isinstance(ack, RaspiAckMsg):
            return None

        data = GPIOChannel().loads(ack.data)
        if not isinstance(data, GPIOChannel):
            return None

        return data.value

    def output(self, channel, value):
        self._transfer(GPIOCtrl(channel=channel, value=value))

    def setup(self, channel, direction, pull_up_down=PUD_OFF, initial=LOW):
        self._transfer(GPIOSetup(channel=channel, direction=direction, pull_up_down=pull_up_down, initial=initial))


class SoftPWM(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, address, mode, channel, frequency, timeout=1):
        super(SoftPWM, self).__init__(address, timeout)
        self.__state = False
        self._transfer(GPIOSoftPWM(mode=mode, channel=channel, frequency=frequency))
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, '{0:d},{1:d},{2:d}'.format(mode, channel, frequency)))

    def __del__(self):
        self.stop()

    def start(self, duty):
        ret = self._transfer(GPIOSoftPWMCtrl(uuid=self.uuid, duty=duty))
        self.__state = ret.ack if isinstance(ret, RaspiAckMsg) else False

    def stop(self):
        ret = self._transfer(GPIOSoftPWMCtrl(uuid=self.uuid))
        self.__state = False if isinstance(ret, RaspiAckMsg) and ret.ack else self.__state

    def is_running(self):
        return self.__state
