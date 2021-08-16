#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import json
from raspi_io import UpdateAgent
from raspi_io.utility import scan_server


if __name__ == "__main__":
    # Get raspberry address
    raspberry_pi = scan_server()[0]

    # Load auth from json an get software name
    auth = json.loads(open('auth.json', 'rb').read())
    software_name = auth.pop("software_name")
    software_install = auth.pop("software_install")

    # Create a software update agent instance
    agent = UpdateAgent(raspberry_pi, timeout=30)

    # Online fetch software newest release
    release = agent.fetch(auth, software_name)
    print(release)

    # Online update
    print(agent.download(auth, release, '/tmp'))

    # Local update
    print(agent.update_from_local("release.tar", "/tmp"))

    print(agent.get_software_version(*tuple(software_install)))