docker run --net="host" -d  --name writeit  -v $PA_SRC:/src -v $PA_INIT:/init --volumes-from data writeit sh /init/writeit-init.sh
