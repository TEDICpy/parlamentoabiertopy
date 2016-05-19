echo "Starting Legislative service..."
docker run --net="host" -d  --name legislative -v $PA_SRC:/src -v $PA_INIT:/init -v $PA_BILLIT_REP:$PA_BILLIT_GEM -v $PA_POPIT_REP:$PA_POPIT_GEM --volumes-from data legislative sh /init/legislative-init.sh
