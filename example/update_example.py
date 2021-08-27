#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import json
from raspi_io import AppManager
from raspi_io.utility import scan_server


if __name__ == "__main__":
    # Get raspberry address
    raspberry_pi = scan_server()[0]

    # Load auth from json an get app name and online update repo name
    auth = json.loads(open('auth.json', 'rb').read())

    app_name = auth.pop("app_name")
    online_update_repo = auth.pop("online_update_repo")

    # Create a AppManager instance
    agent = AppManager(raspberry_pi, timeout=30)

    # Online fetch app newest release
    repo_release_info, software_release_info = agent.fetch_update(auth, online_update_repo)
    print(repo_release_info)
    print(software_release_info)

    # Online update
    print(agent.online_update(auth, repo_release_info, app_name))

    # Local update
    print(agent.local_update("release.tar", app_name))

    for app_name in agent.get_app_list():
        print(agent.get_app_state(app_name))
