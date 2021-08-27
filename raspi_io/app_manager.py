# -*- coding: utf-8 -*-
from .client import RaspiWsClient
from .core import RaspiBaseMsg, RaspiException, RaspiMsgDecodeError
__all__ = ['AppManager', 'AppDescription', 'InstallApp', 'UninstallApp', 'AppState', 'GetAppState',
           'UpdateServerAuth', 'FetchUpdate', 'OnlineUpdate', 'LocalUpdate']


class AppState(RaspiBaseMsg):
    _properties = {'app_name', 'version', 'release_date', 'md5', 'size', 'state'}


class AppDescription(RaspiBaseMsg):
    _properties = {'app_name', 'exe_name', 'autostart', 'boot_args', 'log_file', 'conf_file'}

    def __init__(self, **kwargs):
        kwargs.setdefault('log_file', '')
        kwargs.setdefault('conf_file', '')
        kwargs.setdefault('boot_args', '')
        super(AppDescription, self).__init__(**kwargs)


class UpdateServerAuth(RaspiBaseMsg):
    _properties = {'host', 'username', 'password'}


class InstallApp(RaspiBaseMsg):
    _handle = 'install_app'
    _properties = {'app_desc', 'package'}


class UninstallApp(RaspiBaseMsg):
    _handle = 'uninstall_app'
    _properties = {'app_name'}


class FetchUpdate(RaspiBaseMsg):
    _handle = 'fetch_update'
    _properties = {'auth', 'repo_name', 'newest'}


class OnlineUpdate(RaspiBaseMsg):
    _handle = 'online_update'
    _properties = {'auth', 'release', 'app_name', 'timeout'}


class LocalUpdate(RaspiBaseMsg):
    _handle = 'local_update'
    _properties = {'package', 'app_name'}


class GetAppState(RaspiBaseMsg):
    _handle = 'get_app_state'
    _properties = {'app_name'}


class GetAppList(RaspiBaseMsg):
    _handle = 'get_app_list'


class AppManager(RaspiWsClient):
    PATH = __name__.split(".")[-1]
    IO_SERVER_NAME = 'raspi_io_server'

    def __init__(self, host, timeout=1, verbose=1):
        """Init an app manager

        :param host: raspi-io server address
        :param timeout: raspi-io timeout unit second
        :param verbose: verbose message output
        """
        super(AppManager, self).__init__(host, self.PATH, timeout, verbose)

    @staticmethod
    def check_auth(auth):
        try:
            UpdateServerAuth(**auth)
        except (TypeError, RaspiMsgDecodeError) as e:
            raise RaspiException("Invalid auth: {!r}".format(e))

    def install(self, package, **kwargs):
        """Install an app

        :param package: App install package(tar format same as local update package)
        :param kwargs: AppDescription app description(app_name, exe_name, autostart is required)
        :return: success return true, failed raise exception
        """
        try:
            app_desc = AppDescription(**kwargs)
        except (TypeError, RaspiMsgDecodeError) as e:
            raise RaspiException('Invalid app description: {!r}'.format(e))

        # First send app install package to remote
        filename = self.send_binary_file(package)

        # Require remote install app and get app release info
        return self.check_result(self._transfer(InstallApp(app_desc=app_desc.dict, package=filename)))

    def uninstall(self, app_name):
        """Uninstall app

        :param app_name: uninstall app name
        :return: success return true, failed raise exception
        """
        return self.check_result(self._transfer(UninstallApp(app_name=app_name)))

    def fetch_update(self, auth, repo_name, newest=True):
        """Online Fetch app update information

        :param auth: gogs server auth
        :param repo_name: software update repo name on server
        :param newest: if set only fetch newest software info
        :return: success return a tuple(repo release info dict, software release info dict) else None
        """
        self.check_auth(auth)
        return self.check_result(self._transfer(FetchUpdate(auth=auth, repo_name=repo_name, newest=newest)))

    def online_update(self, auth, repo_release_info, app_name, timeout=300):
        """Online download software release and update

        :param auth: gogs server auth
        :param repo_release_info: repo release info, get it from online_fetch_update()[0]
        :param app_name: app name to upgrade
        :param timeout: download timeout in seconds
        :return: success return software release info
        """
        self.check_auth(auth)
        return self.check_result(self._transfer(
            OnlineUpdate(auth=auth, release=repo_release_info, app_name=app_name, timeout=timeout)
        ))

    def local_update(self, package, app_name):
        """Update app from local

        :param package: App update package (tar format, include data package and release info json file)
        :param app_name: app name (same as install name)
        :return: success return true
        """
        # First send local update file to remote
        filename = self.send_binary_file(package)

        # Request update and get software release info
        return self.check_result(self._transfer(LocalUpdate(package=filename, app_name=app_name)))

    def get_app_list(self):
        return self.check_result(self._transfer(GetAppList()))

    def get_app_state(self, app_name):
        """Get app state

        :param app_name: app name
        :return: success return AppState
        """
        return self.check_result(self._transfer(GetAppState(app_name=app_name)))
