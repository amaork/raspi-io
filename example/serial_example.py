#!/usr/bin/env python3.5
import time
from raspi_io import Serial


if __name__ == "__main__":
    cnt = 0
    port = Serial('192.168.1.166', '/dev/ttyUSB0', 115200)
    while True:
        port.write("{0:d}".format(cnt).encode("utf-8"))
        cnt += 1
        time.sleep(0.1)

