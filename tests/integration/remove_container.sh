#!/bin/bash

CONTAINER="pkitest"
DOCKER_NET="pkinet"

docker rm -f ${CONTAINER}
docker network remove ${DOCKER_NET}
