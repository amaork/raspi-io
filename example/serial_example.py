#!/usr/bin/env python3.5
import time
from raspi_io import Serial
import raspi_io.utility as utility


if __name__ == "__main__":
    cnt = 0
    port = Serial(utility.scan_server()[0], '/dev/ttyUSB0', 115200)
    while True:
        port.write("{0:d}".format(cnt).encode("utf-8"))
        cnt += 1
        time.sleep(0.1)

