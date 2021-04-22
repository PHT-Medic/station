# Airflow for PHT Station

## Important Notice

The state of this version can only be used for testing. We have not performed any tests in a production
environment. 

**Important** All passwords are currently stored in clear text in the database, since the `cryptography`
Python module is not going to be installed. We try to fix this ASAP. 

## Introduction

This is an [Apache Airflow](https://airflow.apache.org/) distribution for the PHT Station. Some notable properties
of this distribution are:

* This Airflow distribution comes bundled with PostgreSQL via `docker-compose`. This is the recommended DBMS
  for the PHT Station.
* The used Executor is the `LocalExecutor`.  We **plan** to also support `CeleryExecutor` in the future, but this is currently not the case.

## Requirements

* `docker` and `Docker Compose`
* The following ports are used by Airflow and need to be available on the host:
    - 5432
    - 5555
    - 6379
    - 8080
    - 8081
    - 8793

## Installation 

1. Install `Docker` and `Docker Compose`.

2. Make sure that the ports listed above are available.

3. Create the Docker volume for Postgres using:
    ```shell script
    docker volume create pgdata
    ```

4. Run:
    ```shell script
    docker-compose -f docker-compose-install.yml up -d
    ```

5. In your browser, go to `http://localhost:8081`:
    1. Login using Postgres system, username: `postgres`, password: `postgres`
    2. Create the database `airflow`
    3. Run the following SQL query for creating the user:
        ```postgresql
           CREATE USER airflow PASSWORD '<airflow_password>';
        ```
   4. Grant the user access to the database via this SQL query:
        ```postgresql
          GRANT ALL ON DATABASE airflow TO airflow;
        ```

6. Run:
    ```shell script
       docker-compose -f docker-compose-install.yml down -v --remove-orphans
    ```
   
7. Run `docker-compose pull`

8. Run `docker-compose build --no-cache --pull` 

9. Edit the variable `sql_alchemy_conn` in `config/airflow.cfg` to reflect your Postgres configuration and make sure
    that this is consistent with the `docker-compose.yml` file
    
## Setting up the station environment
1. Open the `docker-compose.yml` file and edit the following values to match the local environment.   
    In the the volumes section of the airflow service edit the the last volume to match the path to the locally stored
    private key in PEM Format.
    ```
    - <station key path>:/opt/private_key.pem
    ```
2. Then edit the following environment variables to match the local configuration. STATION_ID must be consistent to Vault and Harbor.
    - `FHIR_ADDRESS`
    - `FHIR_USER`
    - `FHIR_PW`
    - `HARBOR_USER`
    - `HARBOR_PW`
    - `STATION_ID`
3. In the docker-compose file edit the following environment variables to set the User and password for the airflow web interface
    - `AIRFLOW_USER`
    - `AIRFLOW_PW`

## First Steps with Running Airflow
1. Run `docker-compose up -d`. 
2. Check that the logs do not contain any startup errors with  `docker-compose logs -f`.
3. Go to `http://localhost:8080` and check whether you can see the web frontend of Apache Airflow.
4. Login with the previously set user credentials for the airflow web interface


<!-- 
## RESTful API for Trains
The Station offers an RESTful API that can be consumed by Trains. The documentation of this API is available on Swagger Hub:

https://app.swaggerhub.com/apis/lukaszimmermann/PHT-Train-Station/0.2.0
-->

The [Train Container Library](https://gitlab.com/PersonalHealthTrain/implementations/germanmii/difuture/train-container-library)
is used for processing in the DAGs.

