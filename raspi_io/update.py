# -*- coding: utf-8 -*-
import os.path
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiException, get_binary_data_header, RaspiMsgDecodeError
__all__ = ['UpdateAuth', 'UpdateFetch', 'UpdateDownload', 'UpdateFromLocal', 'UpdateAgent']


class UpdateAuth(RaspiBaseMsg):
    _handle = 'init'
    _properties = {'host', 'username', 'password'}


class UpdateFetch(RaspiBaseMsg):
    _handle = 'fetch'
    _properties = {'auth', 'name', 'newest'}


class UpdateDownload(RaspiBaseMsg):
    _handle = 'download'
    _properties = {'auth', 'release', 'path', 'timeout'}


class UpdateFromLocal(RaspiBaseMsg):
    _handle = 'update_from_local'
    _properties = {'filename', 'update_path'}


class UpdateAgent(RaspiWsClient):
    PATH = __name__.split(".")[-1]

    def __init__(self, host, timeout=1, verbose=1):
        """Init an software update check instance

        :param host: raspi-io server address
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        super(UpdateAgent, self).__init__(host, self.PATH, timeout, verbose)

    @staticmethod
    def check_auth(auth):
        try:
            UpdateAuth(**auth)
        except (TypeError, RaspiMsgDecodeError) as e:
            raise RaspiException("Invalid auth: {!r}".format(e))

    def fetch(self, auth, name, newest=True):
        """Fetch software update information

        :param auth: gogs server auth
        :param name: software name on server
        :param newest: if set only fetch newest software info
        :return: success return software release info dict else None
        """
        self.check_auth(auth)
        return self.check_result(self._transfer(UpdateFetch(auth=auth, name=name, newest=newest)))

    def download(self, auth, release, path, timeout=300):
        """Download software release to path specified path

        :param auth: gogs server auth
        :param release: software release info, get it from fetch()
        :param path: download path
        :param timeout: download timeout in seconds
        :return: success return software release info
        """
        self.check_auth(auth)
        return self.check_result(self._transfer(UpdateDownload(auth=auth, release=release, path=path, timeout=timeout)))

    def update_from_local(self, software, path):
        """Update software from local

        :param software: software release (tar format, include data package and release info json file)
        :param path: software update path
        :return: success return true
        """
        try:
            with open(software, 'rb') as fp:
                data = fp.read()

            fmt = os.path.splitext(software)[-1][1:]
            header = get_binary_data_header(data, fmt, 'receive_binary_file')
        except IOError as e:
            raise RaspiException("Send file error: {}".format(e))

        # First send local update file
        if not self._send_binary_data(header, data):
            raise RaspiException("Send file error: {}".format(self.get_error()))

        # Request update and get software release info
        result = self._transfer(UpdateFromLocal(filename="{}.{}".format(header.md5, fmt), update_path=path))
        return self.check_result(result)
