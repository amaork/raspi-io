import time
import raspi_io.utility as utility


if __name__ == "__main__":
    print("Host address:{}".format(utility.get_host_address()))
    start = time.time()
    print("Lan raspi-io server:{}".format(utility.scan_server(0.01)))
    print("Scan lan raspi-io server spent:{} second".format(time.time() - start))
