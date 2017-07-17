# -*- coding: utf-8 -*-
import sys
import os.path
import setuptools

root_dir = os.path.abspath(os.path.dirname(__file__))

readme_file = os.path.join(root_dir, 'README.md')
with open(readme_file) as f:
    long_description = f.read()

version_module = os.path.join(root_dir, 'raspi_io', 'version.py')
with open(version_module) as f:
    exec(f.read())

py_version = sys.version_info[:2]

if py_version < (2, 7):
    raise Exception("raspi_io requires Python >= 2.7")

packages = ['raspi_io']


setuptools.setup(
    name='raspi_io',
    version=version,
    description="Using socket.io control your raspberry pi",
    long_description=long_description,
    url='https://github.com/amaork/raspi-io',
    author='Amaork',
    author_email='amaork@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    packages=packages,
    install_requires=['websocket_client']
)