# -*- coding: utf-8 -*-
from .core import RaspiBasicMsg
from .client import RaspiWsClient
__all__ = ['GPIO', 'GPIOEvent', 'GPIOChannel', 'GPIOCtrl', 'GPIOSetup', 'GPIOMode']


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


class GPIO(RaspiWsClient):
    PATH = __name__

    BCM = GPIOMode.BCM
    BOARD = GPIOMode.BOARD

    IN = GPIOSetup.IN
    OUT = GPIOSetup.OUT

    LOW = GPIOCtrl.LOW
    HIGH = GPIOCtrl.HIGH

    PUD_UP = GPIOSetup.PUD_UP
    PUD_OFF = GPIOSetup.PUD_OFF
    PUD_DOWN = GPIOSetup.PUD_DOWN

    def __init__(self, host, timeout=1):
        super(GPIO, self).__init__(host, timeout)

    def setmode(self, mode):
        self.send(GPIOMode(mode=mode))

    def input(self, channel):
        self.send(GPIOChannel(channel=channel))
        data = GPIOChannel().loads(self.recv())
        if not isinstance(data, GPIOChannel):
            return None

        return data.value

    def output(self, channel, value):
        self.send(GPIOCtrl(channel=channel, value=value))

    def setup(self, channel, direction, pull_up_down=PUD_OFF, initial=LOW):
        self.send(GPIOSetup(channel=channel, direction=direction, pull_up_down=pull_up_down, initial=initial))
