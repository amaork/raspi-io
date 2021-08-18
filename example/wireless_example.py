# -*- coding: utf-8 -*-
from raspi_io import Wireless
import raspi_io.utility as utility


if __name__ == "__main__":
    wireless = Wireless(utility.scan_server()[0], verbose=2)
    print(wireless.get_networks())
    # wireless.join_network(ssid="Linksys00681", psk="kgigq0krvg", key_mgmt="WPA-PSK")
    # wireless.leave_network("TEST")