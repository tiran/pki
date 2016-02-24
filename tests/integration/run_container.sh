#!/bin/bash
set -e

IMAGE="dogtagpki/pki-ci-containers:f25_104"
CONTAINER="pkitest"
HOSTNAME="pki.test"
DOCKER_NET="pkinet"
DOCKER_NETRANGE="172.142.142.0/24"
CONTAINER_IP="172.142.142.142"

CURDIR=$(pwd)
SCRIPTDIR="/tmp/workdir/pki/.travis"

if [ ! -d ${CURDIR}/.travis ]; then
    echo "${CURDIR}/.travis"
    echo "$0 must be executed in pki root directory"
    exit 1
fi

# network
docker network inspect ${DOCKER_NET} || \
    docker network create --subnet ${DOCKER_NETRANGE} ${DOCKER_NET}

docker pull ${IMAGE}
docker run \
    --detach \
    --name=${CONTAINER} \
    --hostname=${HOSTNAME} \
    --net ${DOCKER_NET} \
    --ip ${CONTAINER_IP} \
    --expose=389 \
    --expose=8080 \
    --expose=8443 \
    --privileged \
    --tmpfs /tmp \
    --tmpfs /run \
    -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
    -v ${CURDIR}:/tmp/workdir/pki \
    -e BUILDUSER_UID=$(id -u) \
    -e BUILDUSER_GID=$(id -g) \
    -ti \
    ${IMAGE}

docker exec -ti ${CONTAINER} ${SCRIPTDIR}/00-init
docker exec -ti ${CONTAINER} ${SCRIPTDIR}/10-compose-rpms
docker exec -ti ${CONTAINER} ${SCRIPTDIR}/20-install-rpms
docker exec -ti ${CONTAINER} ${SCRIPTDIR}/30-setup-389ds
docker exec -ti ${CONTAINER} ${SCRIPTDIR}/40-spawn-ca
docker exec -ti ${CONTAINER} ${SCRIPTDIR}/50-spawn-kra

# export admin cert
mkdir -p build
docker exec -ti ${CONTAINER} openssl pkcs12 \
    -in /root/.dogtag/${CONTAINER}/ca_admin_cert.p12 \
    -out /tmp/workdir/pki/tests/integration/ca_admin_cert.pem \
    -nodes -passin pass:Secret.123

echo "Dogtag is listening on https://${CONTAINER_IP}:8443/"
echo "To remove the container: docker rm -rf ${CONTAINER}"

if ! $(grep -q ${CONTAINER_IP} /etc/hosts); then
    echo "Add to /etc/hosts:"
    echo "${CONTAINER_IP} ${HOSTNAME}"
fi
