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

* Install `Docker` and `Docker Compose`. 
* Make sure that the ports listed above are available.
* Edit the variable `sql_alchemy_conn` to reflect your Postgres configuration and make sure
  that this is consistent with the `docker-compose.yml` file
* Run `docker-compose build --no-cache --pull`
* Run `docker-compose pull`

## Running Airflow

Run `docker-compose up -d`. 

Check that the logs do not contain any startup errors with  `docker-compose logs -f`.

