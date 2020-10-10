#!/bin/bash

name = $1

docker build -t lab4-img:v2 .
docker run -d -p 0:8080 lab4-img:v2

host_port=$(docker inspect $name | jq '.[].NetworkSettings.Ports."8080/tcp"[].HostPort')
host_port="${host_port%\"}"
host_port="${host_port#\"}"

echo Your application is now available at http://localhost:$host_port