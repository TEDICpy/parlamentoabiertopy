#!/bin/bash
set -e

cont=billit
while true; do
    docker wait $cont;
    docker start $cont;
    sleep 1;
done
