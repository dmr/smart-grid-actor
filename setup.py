#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='Smart-Grid-Actor',
    version='0.4',
    url='https://github.com/dmr/smart-grid-actor',
    license='MIT',
    author='Daniel Rech',
    author_email='danielmrech@gmail.com',
    description='An implementation for a Smart Grid Actor',
    long_description=open('README.md').read(),

    packages=['smart_grid_actor'],

    entry_points={
        'console_scripts': [
            'smart_grid_actor = smart_grid_actor:main',
        ],
    },

    zip_safe=False,
    platforms='any',

    install_requires=[
        'argparse',
        'eventlet',

        'spec', # for tests
        'requests', # for tests
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ]
)
