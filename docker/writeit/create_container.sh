docker create  --name writeit \
    --volumes-from data \
    writeit \
    sh /write-it/init.sh
