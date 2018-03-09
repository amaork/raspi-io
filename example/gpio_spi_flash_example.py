import time
import hashlib
from raspi_io import GPIOSPIFlash
from raspi_io.utility import scan_server
from raspi_io.spi_flash import SPIFlashInstruction


if __name__ == "__main__":
    flash_instruction = SPIFlashInstruction(chip_erase=0x60)
    flash = GPIOSPIFlash(scan_server()[0], 256, 1024*1024, instruction=flash_instruction)
    mid, did = flash.probe()
    print("Manufacturer id:0x{0:02x}, device id:0x{1:04x}".format(mid, did))

    # Read chip
    start = time.time()
    data = flash.read_chip()
    read_md5 = hashlib.md5(data).hexdigest()
    print("Read chip spent:{}, md5:{}".format(time.time() - start, read_md5))

    # Write chip
    verify = True
    start = time.time()
    result = flash.write_chip(data, verify=verify)
    print("Write chip:{}, verify:{}, spent:{}".format(result, verify, time.time() - start))
