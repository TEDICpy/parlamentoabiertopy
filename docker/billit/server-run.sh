echo "Starting Bill-it service..."
docker run --net="host" -d --name billit  -v $PA_SRC:/src -v $PA_INIT:/init --volumes-from data billit sh /init/billit-init.sh
