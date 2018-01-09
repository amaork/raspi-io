import time
import raspi_io.utility as utility
from raspi_io import MmalGraph, TVService


if __name__ == '__main__':
    # Scan get first server address
    server_addr = utility.scan_server()[0]

    tv = TVService(server_addr)
    graph = MmalGraph(server_addr, MmalGraph.HDMI)
    print("Display number:{}".format(graph.display_num))

    # Turn on
    tv.set_preferred()
    patterns = ("../tests/superwoman.jpg", "../tests/cross.png")
    for i in range(10):
        start = time.time()
        print(graph.open(patterns[i % len(patterns)]), graph.is_open, graph.uri)
        print('TIME: ', time.time() - start)
        time.sleep(1)

