#!/usr/bin/env python3.5
import six
from raspi_io import SPI, Query

if __name__ == "__main__":
    address = "192.168.1.166"
    query = Query(address)
    spi = SPI(address, query.get_spi_list()[-1], max_speed=8000)
    data = spi.xfer([0x9f], 3)
    print(list(data), map(six.byte2int, data))
