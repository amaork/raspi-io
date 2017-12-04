#!/usr/bin/env python3.5
from raspi_io import SPI, Query
import raspi_io.utility as utility


if __name__ == "__main__":
    address = utility.scan_server()[0]
    query = Query(address)
    spi = SPI(address, query.get_spi_list()[-1], max_speed=8000)
    data = spi.xfer([0x9f], 3)
    spi.print_binary(data)
