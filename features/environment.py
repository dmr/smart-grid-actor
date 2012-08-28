def after_scenario(context, scenario):
    if hasattr(context, 'servers') and context.servers:
        for p in context.servers:
            p.terminate()
            p.join() # frees up the socket for next scenario
        del context.servers

    for key in context.__dict__.keys():
        assert key.startswith('_'), key

    #import psutil
    #import os
    #psutil_p = psutil.Process(os.getpid()) #os.getppid() <-- subprocesses!
    #print psutil_p.name
    #print [x for x in psutil_p.get_connections() if x.status == 'LISTEN']
    #time.sleep(.1)
    #print [x for x in psutil_p.get_connections() if x.status == 'LISTEN']
