How to install on debian

1. git clone https://github.com/dmr/smart_grid_simulation.git
2. cd smart_grid_simulation
3. install python-setuptools
4. wget http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.7.tar.gz
5. tar -zxf virtualenv.1.7.tar.gz
6. python virtualenv.1.7/virtualenv.py virtualenv
7. source virtualenv/bin/activate
8. rm -R virtualenv-1.7
9. pip install pip -U
10. aptitude install gcc python-dev libevent-dev
10. pip install -r requirements.txt
