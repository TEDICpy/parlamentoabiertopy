#mkdir /data/db
/usr/bin/mongod &
sleep 10

/etc/init.d/elasticsearch start
sleep 3

cd $popit && npm start > popit.log


