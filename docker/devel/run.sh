##create container
docker run -ti --rm --name devel --volumes-from data --volumes-from popit -v /src  --net="host"  devel /bin/bash
