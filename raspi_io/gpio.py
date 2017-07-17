# -*- coding: utf-8 -*-
import uuid
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg
__all__ = ['GPIO', 'GPIOEvent', 'GPIOChannel', 'GPIOCtrl', 'GPIOSetup', 'GPIOMode', 'GPIOCleanup',
           'SoftPWM', 'GPIOSoftPWM', 'GPIOSoftPWMCtrl']


class GPIOMode(RaspiBaseMsg):
    BCM = 11
    BOARD = 10
    _handle = 'setmode'
    _properties = {'mode'}

    def __init__(self, **kwargs):
        super(GPIOMode, self).__init__(**kwargs)


class GPIOCtrl(RaspiBaseMsg):
    LOW = 0
    HIGH = 1
    _handle = 'output'
    _properties = {'channel', 'value'}

    def __init__(self, **kwargs):
        super(GPIOCtrl, self).__init__(**kwargs)


class GPIOEvent(RaspiBaseMsg):
    # Edge
    RISING = 31
    FALLING = 32
    BOTH = 33
    _handle = 'event'
    _properties = {'channel', 'edge', 'callback'}

    def __init__(self, **kwargs):
        kwargs.setdefault('edge', None)
        kwargs.setdefault('callback', None)
        super(GPIOEvent, self).__init__(**kwargs)


class GPIOSetup(RaspiBaseMsg):
    # Direction
    IN = 1
    OUT = 0

    # Pull up down
    PUD_DOWN = 21
    PUD_OFF = 20
    PUD_UP = 22
    _handle = 'setup'
    _properties = {'channel', 'direction', 'pull_up_down', 'initial'}

    def __init__(self, **kwargs):
        kwargs.setdefault('initial', GPIOCtrl.LOW)
        kwargs.setdefault('pull_up_down', GPIOSetup.PUD_OFF)
        super(GPIOSetup, self).__init__(**kwargs)


class GPIOCleanup(RaspiBaseMsg):
    _handle = 'cleanup'
    _properties = {'channel'}

    def __init__(self, **kwargs):
        super(GPIOCleanup, self).__init__(**kwargs)


class GPIOChannel(RaspiBaseMsg):
    _handle = 'input'
    _properties = {'channel', 'value'}

    def __init__(self, **kwargs):
        kwargs.setdefault('value', 0)
        super(GPIOChannel, self).__init__(**kwargs)


class GPIOSoftPWM(RaspiBaseMsg):
    _handle = 'pwm_init'
    _properties = {'mode', 'channel', 'frequency'}

    def __init__(self, **kwargs):
        super(GPIOSoftPWM, self).__init__(**kwargs)


class GPIOSoftPWMCtrl(RaspiBaseMsg):
    _handle = 'pwm_ctrl'
    _properties = {'uuid', 'duty'}

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

    def __init__(self, address, timeout=1, verbose=1):
        super(GPIO, self).__init__(address, timeout, verbose)
        self.__registered = set()

    def __del__(self):
        self.cleanup(list(self.__registered))

    def setmode(self, mode):
        ret = self._transfer(GPIOMode(mode=mode))
        return True if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def input(self, channel):
        ack = self._transfer(GPIOChannel(channel=channel))
        if not isinstance(ack, RaspiAckMsg) or not ack.ack:
            return None

        return ack.data

    def cleanup(self, channel):
        ret = self._transfer(GPIOCleanup(channel=channel))
        return True if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def output(self, channel, value):
        ret = self._transfer(GPIOCtrl(channel=channel, value=value))
        return True if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def setup(self, channel, direction, pull_up_down=PUD_OFF, initial=LOW):
        ret = self._transfer(
            GPIOSetup(channel=channel, direction=direction, pull_up_down=pull_up_down, initial=initial)
        )
        # Setup success register gpio channel
        if isinstance(ret, RaspiAckMsg) and ret.ack:
            if isinstance(channel, (list, tuple)):
                [self.__registered.add(c) for c in channel]
            else:
                self.__registered.add(channel)

        return True if isinstance(ret, RaspiAckMsg) and ret.ack else False


class SoftPWM(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, address, mode, channel, frequency, timeout=1, verbose=1):
        super(SoftPWM, self).__init__(address, timeout, verbose)
        self.__state = False
        self.__channel = channel
        self._transfer(GPIOSoftPWM(mode=mode, channel=channel, frequency=frequency))
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, '{0:d},{1:d},{2:d}'.format(mode, channel, frequency)))

    def __del__(self):
        self.stop()
        self._transfer(GPIOCleanup(channel=self.__channel))

    def start(self, duty):
        ret = self._transfer(GPIOSoftPWMCtrl(uuid=self.uuid, duty=duty))
        self.__state = ret.ack if isinstance(ret, RaspiAckMsg) else False
        return True if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def stop(self):
        ret = self._transfer(GPIOSoftPWMCtrl(uuid=self.uuid))
        self.__state = False if isinstance(ret, RaspiAckMsg) and ret.ack else self.__state
        return True if isinstance(ret, RaspiAckMsg) and ret.ack else False

    def is_running(self):
        return self.__state
