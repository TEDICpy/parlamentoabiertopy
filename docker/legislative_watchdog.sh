#!/bin/bash
set -e

cont=legislative
while true; do
    docker wait $cont;
    docker start $cont;
    sleep 10;
done
