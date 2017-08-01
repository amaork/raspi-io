#!/usr/bin/env python3.5
import time
from raspi_io import Serial


if __name__ == "__main__":
    cnt = 0
    port = Serial('192.168.1.166', '/dev/ttyS0', 115200, timeout=1)
    while True:
        port.read(1)

