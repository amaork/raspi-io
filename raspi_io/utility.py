# -*- coding: utf-8 -*-
import ifaddr
import socket
import ipaddress
import websocket
from .core import DEFAULT_PORT

try:
    import concurrent.futures
except ImportError:
    import multiprocessing
    from threading import Thread

try:
    from queue import Queue
except ImportError:
    from Queue import Queue
__all__ = ['get_host_address', 'scan_server', 'get_system_nic']


def get_host_address():
    """
    Get host address
    :return: address list
    """
    address_list = set()
    for name, interface in get_system_nic().items():
        if 'VMware' in name or 'VirtualBox' in name:
            continue

        if interface.get('network_prefix') != 24:
            continue

        address_list.add(interface.get('ip'))

    return list(address_list)


def get_system_nic(ignore_loopback=True):
    """Get system network interface controller

    :param ignore_loopback: if set will ignore loopback nic
    :return: dict, {nic_name: nic_attribute}
    """
    interfaces = dict()
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        for ip in adapter.ips:
            try:
                address = ipaddress.ip_address("{}".format(ip.ip))

                if ignore_loopback and address.is_loopback:
                    continue

                if address.version == 4:
                    network = ipaddress.ip_network("{}/{}".format(address, ip.network_prefix), False)
                    interfaces[adapter.nice_name] = dict(
                        ip=str(address),
                        network=str(network),
                        network_prefix=ip.network_prefix
                    )
                    break
            except ValueError:
                continue

    return interfaces


def scan_server(timeout=0.05):
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
        except (websocket.WebSocketTimeoutException, socket.error, OSError):
            return None

    def connect_worker():
        while not in_queue.empty():
            try:
                out_queue.put(connect_device(in_queue.get()))
            finally:
                in_queue.task_done()

    # Get system all network interface controller
    valid_network = list()
    for name, interface in get_system_nic().items():
        if 'VMware' in name or 'VirtualBox' in name:
            continue

        if interface.get('network_prefix') != 24:
            continue

        valid_network.append(interface.get('network'))

    # According to network generate host list
    all_host = list()
    for network in valid_network:
        network = ipaddress.ip_network(network)
        all_host.extend([str(x) for x in network.hosts()])

    try:
        # Python3 using thread pool
        with concurrent.futures.ThreadPoolExecutor() as pool:
            valid_host = filter(lambda x: x is not None, pool.map(connect_device, all_host))
        return list(set(valid_host))
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
