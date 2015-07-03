docker create  --name popit \
    --volumes-from data \
    -p 3000:3000 --net="host" \
    popit \
    sh /popit/init.sh
