#!/bin/bash

docker run \
    -d \
    --name=pg \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    postgres:13.1
