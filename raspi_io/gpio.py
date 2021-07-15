# -*- coding: utf-8 -*-
import uuid
from abc import abstractmethod
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiAckMsg
__all__ = ['GPIO', 'GPIOEvent', 'GPIOChannel', 'GPIOCtrl', 'GPIOSetup', 'GPIOMode', 'GPIOCleanup',
           'SoftSPI', 'GPIOSoftSPI', 'GPIOSoftSPIXfer', 'GPIOSoftSPIRead', 'GPIOSoftSPIWrite',
           'SoftPWM', 'GPIOSoftPWM', 'GPIOSoftPWMCtrl', 'GPIOTimingContentManager']


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


class GPIOSoftSPI(RaspiBaseMsg):
    _handle = 'spi_init'
    _properties = {'mode', 'cs', 'clk', 'mosi', 'miso', 'bits_per_word'}

    def __init__(self, **kwargs):
        super(GPIOSoftSPI, self).__init__(**kwargs)

    def generate_uuid(self):
        return str(uuid.uuid5(uuid.NAMESPACE_OID, "SoftSPI:{0:d},{1:d},{2:d},{3:d},{4:d},{5:d}".format(
            self.mode, self.cs, self.clk, self.mosi, self.miso, self.bits_per_word,
        )))


class GPIOSoftSPIXfer(RaspiBaseMsg):
    _handle = 'spi_xfer'
    _properties = {'data', 'size', 'uuid'}

    def __init__(self, **kwargs):
        super(GPIOSoftSPIXfer, self).__init__(**kwargs)


class GPIOSoftSPIRead(RaspiBaseMsg):
    _handle = 'spi_read'
    _properties = {'size', 'uuid'}

    def __init__(self, **kwargs):
        super(GPIOSoftSPIRead, self).__init__(**kwargs)


class GPIOSoftSPIWrite(RaspiBaseMsg):
    _handle = 'spi_write'
    _properties = {'data', 'uuid'}

    def __init__(self, **kwargs):
        super(GPIOSoftSPIWrite, self).__init__(**kwargs)


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

    def __init__(self, host, timeout=1, verbose=1):
        super(GPIO, self).__init__(host, self.PATH, timeout, verbose)
        self.__registered = set()

    def __del__(self):
        try:
            self.cleanup(list(self.__registered))
        except AttributeError:
            pass

    def setmode(self, mode):
        """Set GPIO mode

        :param mode: GPIOMode.BCM or GPIOMode.BOARD
        :return: success return True failed return False
        """
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
        """Setup channel mode

        :param channel: could be a single pin or multi-pin (list)
        :param direction: pin direction IN or OUT
        :param pull_up_down: PUD_UP/PUD_OFF/PUD_DOWN
        :param initial: initial state
        :return: success return true, failed return false
        """
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

    def __init__(self, host, mode, channel, frequency, timeout=1, verbose=1):
        super(SoftPWM, self).__init__(host, self.PATH, timeout, verbose)
        self.__state = False
        self.__channel = channel
        self._transfer(GPIOSoftPWM(mode=mode, channel=channel, frequency=frequency))
        # TODO: Move to SoftPWM as a function
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, '{0:d},{1:d},{2:d}'.format(mode, channel, frequency)))

    def __del__(self):
        try:
            self.stop()
            self._transfer(GPIOCleanup(channel=self.__channel))
        except AttributeError:
            pass

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


class SoftSPI(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, mode, cs, clk, mosi, miso, bits_per_word=8, timeout=1, verbose=1):
        """Software spi controller, using gpio simulate

        :param host: raspberry ip address
        :param mode: gpio mode, BCM or BOARD
        :param cs: spi chip select gpio pin
        :param clk: spi clk gpio pin
        :param mosi: spi mosi gpio pin
        :param miso: spi miso gpio pin
        :param bits_per_word: spi per word bits
        :param timeout: timeout
        :param verbose: verbose message output
        :return:
        """
        super(SoftSPI, self).__init__(host, self.PATH, timeout, verbose)
        spi = GPIOSoftSPI(mode=mode, cs=cs, clk=clk, mosi=mosi, miso=miso, bits_per_word=bits_per_word)
        ret = self._transfer(spi)
        if not isinstance(ret, RaspiAckMsg) or not ret.ack:
            raise RuntimeError(ret.data)
        self.channel = [cs, clk, mosi, miso]
        self.uuid = spi.generate_uuid()

    def __del__(self):
        try:
            self.close()
        except AttributeError:
            pass

    def xfer(self, data, size=0):
        ret = self._transfer(GPIOSoftSPIXfer(data=data, size=size, uuid=self.uuid))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else list()

    def read(self, size):
        ret = self._transfer(GPIOSoftSPIRead(size=size, uuid=self.uuid))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else list()

    def write(self, data):
        ret = self._transfer(GPIOSoftSPIWrite(data=data, uuid=self.uuid))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else 0

    def close(self):
        ret = self._transfer(GPIOCleanup(channel=self.channel))
        return ret.data if isinstance(ret, RaspiAckMsg) and ret.ack else False


class GPIOTimingContentManager(object):
    def __init__(self, gpio, start, end, verbose=False, ignoreException=False):
        """Using content manager control gpio timing

        :param gpio: GPIO instance will pass to start and end callback
        :param start: start timing callback
        :param end: end timing callback
        :param verbose: show verbose info
        :param ignoreException: ignore exception or not
        """
        if not isinstance(gpio, GPIO):
            raise TypeError('{!} required {!r} type'.format('gpio', GPIO.__name__))

        if not callable(start):
            raise TypeError('{!} required {!r} type'.format('start', 'callable'))

        if not callable(end):
            raise TypeError('{!} required {!r} type'.format('end', 'callable'))

        self.gpio = gpio
        self._end = end
        self._start = start
        self._verbose = verbose
        self._ignoreException = ignoreException

    def __enter__(self):
        if self._verbose:
            print('Start timing')

        self._start(self.gpio)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._verbose:
            print('End timing')

        self._end(self.gpio)
        return self._ignoreException
