docker run --net=host --rm -ti  --name popit  -v /root/devel/src:/src -v /root/devel/parlamentoabiertopy/docker/init:/init --volumes-from data popit sh /init/popit-init.sh
