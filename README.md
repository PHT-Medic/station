[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](https://pht-medic.github.io/documentation/)
[![Discord](https://badgen.net/badge/icon/discord?icon=discord&label)](https://discord.gg/ztdAPzWQ8j)

# PHT Station

This is the collection repository for a PHT-Medic station. It mainly contains an installation script and a configuration
file template. After preconfiguring the configuration file, the installation script can be run to guide you through the further installation steps.

The installation instructions assume the system running under a debian based system. If you are running on a different system, you will need to adapt the installation script or
download the pypi package and use the packaged installer with the given configuration file.

For more detailed instructions visit [documentation](https://pht-medic.github.io/documentation/).


## Introduction
The station software consists of several services:

* A user interface that allows the user to manage the station as well as run and configure trains.
* The station API as central endpoint into the other services
* A postgres database used by airflow and the API
* An [apache airflow](https://airflow.apache.org/) instance that is responsible for executing the trains and other long running tasks
* A [minio](https://minio.io/) instance that is responsible for storing the data sets and models
* Redis for caching
* A [traefik](https://traefik.io/) reverse proxy for tls termination and load balancing, this allows the dynamic addition
of new FHIR project warehouses with TLS enabled.
* Optional blaze fhir server

These services are managed by a docker-compose file, which is created based on your input using a containerized installer.

## Requirements

* `docker` and `docker-compose` need to be installed
* The following ports are used by the station and need to be available on the host:
    - 443
    - 80
* The station can generate self-signed certificates but is recommended to use a certificate signed by a trusted CA for the chosen
domain name. The key and the full-chain should be placed into the `./certs` directory and the files can then be loaded by 
the reverse proxy by setting them either in the installation cli or in the configuration file.

## Setup
Before starting the station installer the station needs be set up in the central user interface and the obtained 
credentials need to be entered into the configuration file.

1. Rename the `station_config.yml.tmpl` to `station_config.yml`
2. Create a station and copy the id listed in the list view in the realm management screen.
3. Copy the station id to the `station_id` variable in the configuration file.
4. Create a new robot for the station and assign it the `station_edit` permission.
5. Copy the `robot id` and `secret` and enter it into the configuration file along with the api url of the central user interface instance (e.g. https://personalhealhtrain.de/api).

## Installation

Install the station by running the following command:
```bash
./install.sh
```
The CLI installer will guide you through the necessary configuration steps.

## Getting Help
Discord : [join our server](https://discord.gg/ztdAPzWQ8j)

Email: pht@medizin.uni-tuebingen.de





