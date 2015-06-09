docker create  --name billit \
    --volumes-from data \
    billit \
    sh /billit/init.sh
