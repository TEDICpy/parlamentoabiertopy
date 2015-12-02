echo "Starting Pop-It service..."
docker run --net="host" -d  --name popit  -v $PA_SRC:/src -v $PA_INIT:/init -v $PA_ESEARCH_LOCAL:/var/lib/elasticsearch/ --volumes-from data popit sh /init/popit-init.sh
