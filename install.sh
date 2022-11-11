#!/bin/bash

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
source $DIR/scripts/common.sh

set +o noglob

usage=$'Please configure your station in the station.yml file before starting the installation
Use --worker to spawn a worker node.
Use --update to update the station software.
'
item=0

# worker node disabled by default
worker=$false
# update the station software
update=$false


while [ $# -gt 0 ]; do
        case $1 in
            --help)
            note "$usage"
            exit 0;;
            --worker)
            worker=true;;
            --update)
            update=true;;
            *)
            note "$usage"
            exit 1;;
        esac
        shift || true
done


workdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $workdir

if [ $worker ]; then
  note "Starting worker node"
  docker-compose -f docker-compose.yml -f docker-compose.worker.yml up -d
  exit 0
fi

if [ $update ]; then
  h2 "Updating station software"
  docker-compose -f docker-compose.yml pull
  h2 "Shutting down station  ..."
  docker-compose down
  h2 "Restarting station..."
  docker-compose up -d
  success $"----The station has been updated successfully.----"
  exit 0
fi

h2 "[Step $item]: checking if docker is installed ..."; ((item+=1))
check_docker

h2 "[Step $item]: checking docker-compose is installed ..."; ((item+=1))
check_dockercompose


if [ -n "$(docker-compose ps -q)"  ]
then
    note "stopping existing station instance ..."
    docker-compose down
fi
echo ""

h2 "[Step $item]: downloading installer ..."; ((item+=1))
echo ""
docker pull ghcr.io/pht-medic/station-ctl:latest

echo ""
h2 "[Step $item]: installing ..."; ((item+=1))
echo ""
docker run -it \
  -v "$(pwd):/mnt/station:rw" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e "PHT_TEMPLATE_DIR=/home/station/station/ctl/templates" \
  ghcr.io/pht-medic/station-ctl:latest install \
  --install-dir /mnt/station \
  --host-path "$(pwd)"
echo ""
success $"----Installation succeeded.----"

h2 "[Step $item]: Starting the station ..."; ((item+=1))
echo ""
docker-compose up -d
echo ""
success $"----The station has been installed and started successfully.----"