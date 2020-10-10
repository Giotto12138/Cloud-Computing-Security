#!/bin/bash

docker build -t lab4-img:v1 .
docker run -d -p 9090:8080 lab4-img:v1

