import time
from raspi_io import MmalGraph, TVService


if __name__ == '__main__':
    tv = TVService("192.168.1.166")
    graph = MmalGraph("192.168.1.166", MmalGraph.HDMI)
    print("Display number:{}".format(graph.display_num))

    # Turn on
    tv.set_preferred()
    patterns = ("../tests/superwoman.jpg", "../tests/cross.png")
    for i in range(10):
        start = time.time()
        print(graph.open(patterns[i % len(patterns)]), graph.is_open, graph.uri)
        print('TIME: ', time.time() - start)
        time.sleep(1)

