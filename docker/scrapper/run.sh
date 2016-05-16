#!/bin/bash
docker run --net="host" -ti --rm --name scrapper -v $PA_SRC:/src scrapper /bin/bash
