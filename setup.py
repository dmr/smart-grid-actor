#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Smart-Grid-Simulation
---------------------

The Simulation I did for my diploma thesis.



Installation
------------

Checkout git and install requirements from requirements.txt, or just use pip

    pip install http://github.com/dmr/smart-grid-simulation.git#egg=smart_grid_simulation


How to install on new debian installation using virtualenv:

- install python-setuptools
- wget http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.7.tar.gz
- tar -zxf virtualenv.1.7.tar.gz
- python virtualenv.1.7/virtualenv.py virtualenv
- source virtualenv/bin/activate
- rm -R virtualenv.1.7.tar.gz virtualenv-1.7
- pip install pip -U
- aptitude install gcc python-dev libevent-dev
- git clone https://github.com/dmr/smart_grid_simulation.git
- cd smart_grid_simulation
- pip install -r requirements.txt
- python setup.py test



Links
`````
* `Documentation <https://github.com/dmr/smart-grid-simulation>`_
* `development version
  <https://github.com/dmr/smart-grid-simulation>`_

"""

from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='Smart-Grid-Simulation',
    version='0.1.1',
    url='https://github.com/dmr/smart-grid-simulation',
    license='MIT',
    author='Daniel Rech',
    author_email='danielmrech@gmail.com',
    description='',
    long_description=__doc__,
    packages=['smart_grid_simulation'],
    scripts=[
        'scripts/smart_grid_simulation',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],

    tests_require=['Attest'],
    test_loader='attest:auto_reporter.test_loader',
    test_suite='tests.sgsim_test'
)