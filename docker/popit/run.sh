docker run --net="host" -d  --name popit  -v $PA_SRC:/src -v $PA_INIT:/init --volumes-from data popit sh /init/popit-init.sh
