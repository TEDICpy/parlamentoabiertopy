docker run --net="host" --rm -ti --name votaciones -v $PA_SRC:/src -v /Data/devel/projects/tedic/src/PAVotaciones/public/:/var/www/html/ --volumes-from data votaciones /bin/bash

