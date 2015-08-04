docker run --net=host --rm -ti --name legislative -v /root/devel/src:/src -v /root/devel/parlamentoabiertopy/docker/init:/init --volumes-from data legislative sh /init/legislative-init.sh
