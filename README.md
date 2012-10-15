Smart-Grid-Actor
----------------

An implementation for a Smart Grid Actor.
The package provides a CLI "smart_grid_actor" to start a Smart Grid Actor Server.


Installation
------------

Checkout git and install requirements from requirements.txt, or just use pip

    pip install git+http://github.com/dmr/smart-grid-actor.git#egg=smart_grid_actor

This will install all dependencies needed and provide the command line utilities
"smart_grid_actor" and "smart_grid_actor_batch_starter".

Start an Actor with

    smart_grid_actor --value-range 1 2 3 4

or many Actors with

    smart_grid_actor_batch_starter --value-range -1 1 2 -n4

Both commands provide more usage information if called with --help.


Tests
-----
To run the tests, install spec and/or nose and requests and run them:

    pip install spec requests
    nosetests
