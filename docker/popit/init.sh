#!/bin/bash
# Lanzo mongodb
nohup /usr/bin/mongod &
sleep 10
# Lanzo elasticsearch
/etc/init.d/elasticsearch start
sleep 3
# Lanzo la app
npm start


