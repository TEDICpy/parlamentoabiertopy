docker run --net="host" --rm -ti --name billit  -v $PA_SRC:/src -v $PA_INIT:/init --volumes-from data billit /bin/bash
