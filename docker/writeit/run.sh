#!/bin/bash
docker run --net="host" --rm -ti  --name writeit  -v $PA_SRC:/src -v $PA_INIT:/init --volumes-from data writeit /bin/bash
