from raspi_io import SoftSPI, GPIO
import raspi_io.utility as utility

if __name__ == "__main__":
    address = utility.scan_server(0.05)[0]
    cpld = SoftSPI(address, GPIO.BCM, cs=7, clk=11, mosi=10, miso=9, bits_per_word=10)
    flash = SoftSPI(address, GPIO.BCM, cs=8, clk=11, mosi=10, miso=9, bits_per_word=8)

    cpld.write([0x0])
    cpld.write([0x10])
    cpld.write([0x30])
    cpld.write([0x80])
    data = flash.xfer([0x9f], 3)
    flash.print_binary(data)
