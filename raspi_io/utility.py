# -*- coding: utf-8 -*-
import socket
import websocket
from queue import Queue
from .core import DEFAULT_PORT

try:
    import concurrent.futures
except ImportError:
    import multiprocessing
    from threading import Thread

__all__ = ['get_host_address', 'scan_server']


def get_host_address():
    """
    Get host address
    :return:
    """
    try:

        for addr in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not addr.startswith("127."):
                return addr

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        return s.getsockname()[0]
    except socket.error:
        return socket.gethostbyname(socket.gethostname())


def scan_server(timeout=0.04):
    """Scan lan raspi_io server

    :param timeout: scan timeout
    :return: server address list
    """
    in_queue = Queue()
    out_queue = Queue()

    def connect_device(address):
        try:
            ws = websocket.create_connection("ws://{}:{}".format(address, DEFAULT_PORT), timeout=timeout)
            ws.close()
            return address
        except (websocket.WebSocketTimeoutException, socket.timeout):
            return None

    def connect_worker():
        while not in_queue.empty():
            try:
                out_queue.put(connect_device(in_queue.get()))
            finally:
                in_queue.task_done()

    # Generate lan host list
    network_seg = ".".join(get_host_address().split(".")[:-1])
    all_host = ["{}.{}".format(network_seg, i) for i in range(255)]

    try:
        # Python3 using thread pool
        with concurrent.futures.ThreadPoolExecutor() as pool:
            valid_host = filter(lambda x: x is not None, pool.map(connect_device, all_host))
        return list(valid_host)
    except NameError:
        # Python 2 using thread + queue
        map(in_queue.put, all_host)
        for _ in range(multiprocessing.cpu_count() * 5):
            th = Thread(target=connect_worker)
            th.setDaemon(True)
            th.start()

        # Wait done
        in_queue.join()
        return filter(lambda x: x, [out_queue.get() for _ in range(out_queue.qsize())])
