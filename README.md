Smart-Grid-Actor
----------------

An implementation for a Smart Grid Actor.
The package provides two command line programs "smart_grid_actor" ans "smart_grid_actor_batch_starter" to start one or many Smart Grid Actor Servers.


Installation
------------

Just use pip:

    pip install git+http://github.com/dmr/smart-grid-actor.git#egg=smart_grid_actor

This will install all dependencies (argparse, bjoern) needed and provide the command line utilities.

Start an Actor with:

    smart_grid_actor --value-range 1 2 3 4

or many Actors with:

    smart_grid_actor_batch_starter --value-range -1 1 2 -n4

Both commands provide more usage information if called with --help.

Alternatively, do a git clone and execute python setup.py install/develop.


Tests
-----

To run the tests, install spec and/or nose and requests and run them:

    pip install spec requests
    nosetests

Thank you http://travis-ci.org for running the tests :)
[![Build Status](https://travis-ci.org/dmr/smart-grid-actor.png)](https://travis-ci.org/dmr/smart-grid-actor)
