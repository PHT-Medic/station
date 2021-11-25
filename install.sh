#!/bin/bash

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
source $DIR/scripts/common.sh

set +o noglob

usage=$'Please configure your station in the station.yml file before starting the installation
Use --worker to spawn a worker node.
'
item=0

# worker node disabled by default
worker=$false


while [ $# -gt 0 ]; do
        case $1 in
            --help)
            note "$usage"
            exit 0;;
            --worker)
            worker=true;;
            *)
            note "$usage"
            exit 1;;
        esac
        shift || true
done


workdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $workdir

h2 "[Step $item]: checking if docker is installed ..."; let item+=1
check_docker

h2 "[Step $item]: checking docker-compose is installed ..."; let item+=1
check_dockercompose

echo ""

if [ -n "$(docker-compose ps -q)"  ]
then
    note "stopping existing station instance ..."
    docker-compose down -v
fi
echo ""

h2 "[Step $item]: starting station ..."
docker-compose up -d

success $"----The station has been installed and started successfully.----"