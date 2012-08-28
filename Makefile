test:
	#pip install behave attest
	#create_ramdisk tmp
	../../code/virtualenv/bin/python tests/__init__.py -t tmp
	#remove_ramdisk tmp
	behave --stop