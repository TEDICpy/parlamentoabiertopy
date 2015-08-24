docker run --net="host" --rm -ti  --name legislative -v $PA_SRC:/src -v $PA_INIT:/init -v $PA_BILLIT_REP:$PA_BILLIT_GEM -v $PA_POPIT_REP:$PA_POPIT_GEM --volumes-from data legislative /bin/bash
