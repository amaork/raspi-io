import time
from raspi_io import TVService
import raspi_io.utility as utility


if __name__ == "__main__":
    tv = TVService(utility.scan_server()[0])

    # Get status
    print(tv.get_status())

    # Get preferred mode
    print(tv.get_preferred_mode())

    # Get support modes
    for group in (TVService.DMT, TVService.CEA):
        for mode in tv.get_modes(group):
            print(mode)

    # Set explicit mode, 1440x90
    tv.set_explicit(TVService.DMT, 47)

    # Wait monitor respond
    time.sleep(3)

    # Set preferred mode
    tv.set_preferred()
