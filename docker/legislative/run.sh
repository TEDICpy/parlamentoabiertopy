docker run --name legislative -d --volumes-from data --net="host" -v /src legislative /bin/bash
