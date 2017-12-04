#!/usr/bin/env python3.5
from raspi_io import Query
import raspi_io.utility as utility


if __name__ == "__main__":
    q = Query(utility.scan_server()[0])
    print("Hardware info:{}".format(q.get_hardware_info()))
    for iface in q.get_iface_list():
        print("Ethernet interface:{}:{}".format(iface, q.get_ethernet_addr(iface)))
    print("I2C device list:{}".format(q.get_i2c_list()))
    print("SPI device list:{}".format(q.get_spi_list()))
    print("Serial port list{}".format(q.get_serial_list(include_links=True)))
    print("MMC block:{}".format(q.get_device_list("mmcblk*")))
