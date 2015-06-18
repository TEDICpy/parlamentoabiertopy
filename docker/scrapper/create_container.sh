docker create  --name scrapper \
    --volumes-from data \
    --link popit:popit
    scrapper \
    cd parlamentoabiertopy/scrapper && python scrapper.py all

