docker create  --name billit \
       --volumes-from data \
       -v /src \
       --net="host" \
       billit \
       sh /src/bill-it/init.sh


#       -e billit=billit  \
