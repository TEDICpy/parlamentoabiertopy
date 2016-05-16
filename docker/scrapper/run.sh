 docker run --net="host" --rm --name scrapper -ti -v $PA_SRC:/src --volumes-from data scrapper /bin/bash
