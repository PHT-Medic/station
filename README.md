# PHT Station

## Introduction

This is an [Apache Airflow](https://airflow.apache.org/) distribution for the PHT Station. Some notable properties
of this distribution are:

* This Airflow distribution comes bundled with PostgreSQL via `docker-compose`. This is the recommended DBMS
  for the PHT Station.
* The used Executor is the `LocalExecutor`.  We **plan** to also support `CeleryExecutor` in the future, but this is currently not the case.

The [Train Container Library](https://github.com/PHT-Medic/train-container-library.git)
is used for processing trains in the DAGs.

## Requirements

* `docker` and `docker-compose` need to be installed
* The following ports are used by the station and need to be available on the host:
    - 5432
    - 8080

## Setting up the station environment

Open the `.env` file at the root of the repository and edit the following environment variables to match the local configuration. STATION_ID must be consistent to Vault and Harbor.
- `FHIR_ADDRESS` the address of the default fhir server connected to the station (this can also be configured per train)
- `FHIR_USER` username to authenticate against the FHIR server using Basic Auth
- `FHIR_PW` password for Basic Auth
- `FHIR_TOKEN` Token to authenticate against the FHIR server using Bearer Token
- `CLIENT_ID` identifier of client with permission to access the fhir server 
- `CLIENT_SECRET` secret of above client to authenticate against the provider
- `OIDC_PROVIDER_URL` token url of Open ID connect provider e.g. keycloak, that is configured for the FHIR server
- `FHIR_SERVER_TYPE` the type of fhir server (PHT FHIR client supports IBM, Hapi and Blaze FHIR servers)
- `HARBOR_API_URL` the url of the central harbor instance
- `HARBOR_USER` username to authenticate against harbor
- `HARBOR_PW` password to authenticate against harbor
- `STATION_ID` Chosen identifier of the station (match central UI configuration)
- `STATION_PRIVATE_KEY_PATH` path to the private key on the local filesystem that should be mounted as a volume
- `AIRFLOW_USER` admin user to be created for the airflow instance 
- `AIRFLOW_PW` password for the airflow admin user
- `STATION_DATA_DIR` the absolute path of the directory where the station stores the input data for trains, this path is
also used by the FHIR client to store the query results before passing them to trains


## Installation 

1. Install `docker` and `docker-compose` if not already installed.

2. Make sure that the ports listed above are available.

3. Create the Docker volume for Postgres using:
    ```shell script
    docker volume create pg_station
    ```

4. Run:
    ```shell script
    docker-compose build
    ```
## Troubleshooting   

1. Problemes with ```docker-compose build``` can be bypassed by pulling a pre-built image. 
For this, the line " build: './airflow' "  in the docker-compose.yml file has to be replaced with " image: 'ghcr.io/pht-medic/station-airflow:latest' "
   

## First Steps with running the station
1. Run `docker-compose up -d`. 
2. Check that the logs do not contain any startup errors with  `docker-compose logs -f`.
3. Go to `http://localhost:8080` and check whether you can see the web interface of Apache Airflow.
4. Login to the airflow web interface with the previously set user credentials




