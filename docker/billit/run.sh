docker run --net=host --rm -ti  --name billit  -v /root/devel/src:/src -v /root/devel/parlamentoabiertopy/docker/init:/init --volumes-from data billit sh /init/billit-init.sh
