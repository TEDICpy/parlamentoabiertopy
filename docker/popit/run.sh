docker run --net="host" --rm -ti  --name popit  -v $PA_SRC:/src -v $PA_INIT:/init  --volumes-from data popit /bin/bash
