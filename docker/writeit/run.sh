docker run --net=host --rm -ti  --name writeit  -v /root/devel/src:/src -v /root/devel/parlamentoabiertopy/docker/init:/init --volumes-from data writeit sh /init/writeit-init.sh
