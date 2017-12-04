#!/usr/bin/env python3.5
from raspi_io import Serial
import raspi_io.utility as utility


if __name__ == "__main__":
    cnt = 0
    port = Serial(utility.scan_server()[0], '/dev/ttyS0', 115200, timeout=1)
    while True:
        port.read(1)
