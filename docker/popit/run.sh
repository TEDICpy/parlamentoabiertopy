docker run --net="host" --rm -ti --name popit -v $PA_SRC:/src -v $PA_INIT:/init -v $PA_ESEARCH_LOCAL:$PA_ESEASRCH_CONTAINER --volumes-from data popit /bin/bash

