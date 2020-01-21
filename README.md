# Airflow for PHT Station

## Important Notice

The state of this version can only be used for testing. We have not performed any tests in a production
environment. 

**Important** All passwords are currently stored in clear text in the database, since the `cryptography`
Python module is not going to be installed. We try to fix this ASAP. 

## Introduction

This is an [Apache Airflow](https://airflow.apache.org/) distribution for the PHT Station. Some notable properties
of this distribution are:

* This Airflow distribution comes bundled with Postgres via `docker-compose`. This is the recommended DBMS
  for the PHT Station.
* The used Executor is the `LocalExecutor`.  We **plan** to also support `CeleryExecutor` in the future.
* This distribution comes with an additional HTTP service, exposed on the Airflow container on port 4000.
  This is supposed to be a temporary solution until Apache Airflow 2 is released, which will have an
  [overhauled REST API](https://cwiki.apache.org/confluence/display/AIRFLOW/Airflow+2.0). 

## Requirements

* `docker` and `Docker Compose`
* The following ports are used by Airflow and need to be available on the host:
    - 4000
    - 5432
    - 5555
    - 6379
    - 8080
    - 8081
    - 8793

## Installation 

1. Install `Docker` and `Docker Compose`.

2. Make sure that the ports listed above are available.

3. Create the Docker Network `pht-station` using:
    ```shell script
    docker network create pht-station
    ```

4. Create the Docker volume for Postgres using:
    ```shell script
    docker volume create pgdata
    ```
5. Run:
    ```shell script
    docker-compose -f docker-compose-install.yml up -d
    ```
6. In your browser, go to `http://localhost:8081`:
    1. Login using Postgres system, username: `postgres`, password: `postgres`
    2. Create the database `airflow`
    3. Run the following command for creating the user:
        ```postgresql
           CREATE USER airflow PASSWORD '<airflow_password>';
        ```
   4. Grant the user access to the database:
        ```postgresql
          GRANT ALL ON DATABASE airflow TO airflow;
        ```
7. Run:
    ```shell script
       docker-compose -f docker-compose-install.yml down -v --remove-orphans
    ```
   
8. Run `docker-compose pull`

9. Run `docker-compose build --no-cache --pull` 

10. Edit the variable `sql_alchemy_conn` in `config/airflow.cfg` to reflect your Postgres configuration and make sure
    that this is consistent with the `docker-compose.yml` file

## Running Airflow
1. Run `docker-compose up -d`. 
2. Check that the logs do not contain any startup errors with  `docker-compose logs -f`.
3. Go to `http://localhost:8080` and check whether you can see the web frontend of Apache Airflow.
4. Run the DAG `test_docker` to see whether DAGs generally have access to the Docker daemon.

## Published Ports
The following TCP ports are used by this application stack:

Port | Service (Docker Compose) | Description
-----|--------------------------|----------------------------------------
4000 | `airflow`                | Something Airflow related. I don't know.
5432 | `db`                     | Postgres DBMS
5555 | `airflow`                | Something Airflow related. I don't know.
6379 | `redis`                  | The Redis port
8080 | `airflow`                | Airflow Web Interface
8081 | `adminer`                | Adminer for database administration
8793 | `airflow`                |  Something Airflow related. I don't know.
