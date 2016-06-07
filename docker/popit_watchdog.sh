#!/bin/bash
set -e

cont=popit
while true; do
    docker wait $cont;
    docker start $cont;
    sleep 1;
done
