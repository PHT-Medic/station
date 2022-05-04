# PHT Station

This is the collection repository for a PHT-Medic station. It contains an airflow instance for processing train images
and can be configured via environment variables. Further information can be found in
the [documentation](https://pht-medic.github.io/documentation/) or on our [website](https://personalhealthtrain.de).

## Introduction
The current stable version includes a docker-compose based [Apache Airflow](https://airflow.apache.org/) distribution with DAGs for executing trains as well as the
associated postgres database.
In the DAGs the [Train Container Library](https://github.com/PHT-Medic/train-container-library.git)
is used for processing trains in the DAGs.

## Requirements

* `docker` and `docker-compose` need to be installed
* The following ports are used by the station and need to be available on the host:
    - 5432
    - 8080

## Setting up the station environment
Copy the `.env.tmpl` file at the root of the repository to `.env` to configure your local environment.  
Open the `.env` file and edit the following environment variables to match the local
configuration. STATION_ID must be consistent to Vault and Harbor.
- `STATION_ID` Chosen identifier of the station (match central UI configuration)
- `STATION_PRIVATE_KEY_PATH` path to the private key on the local filesystem that should be mounted as a volume
- `PRIVATE_KEY_PASSWORD` optional password for the private key if it is encrypted
- `AIRFLOW_USER` admin user to be created for the airflow instance
- `AIRFLOW_PW` password for the airflow admin user
- `HARBOR_URL` the url of the central harbor instance
- `HARBOR_USER` username to authenticate against harbor
- `HARBOR_PW` password to authenticate against harbor
- `STATION_DATA_DIR` the absolute path of the directory where the station stores the input data for trains, this path is
  also used by the FHIR client to store the query results before passing them to trains
- `FHIR_ADDRESS` (Optional) the address of the default fhir server connected to the station (this can also be configured per train)
- `FHIR_USER` (Optional) username to authenticate against the FHIR server using Basic Auth
- `FHIR_PW` (Optional) password for FHIR server Basic Auth
- `FHIR_TOKEN` (Optional) Token to authenticate against the FHIR server using Bearer Token
- `CLIENT_ID` (Optional) identifier of client with permission to access the fhir server
- `CLIENT_SECRET` (Optional) secret of above client to authenticate against the provider
- `OIDC_PROVIDER_URL` (Optional) token url of Open ID connect provider e.g. keycloak, that is configured for the FHIR server
- `FHIR_SERVER_TYPE` (Optional) the type of fhir server (PHT FHIR client supports IBM, Hapi and Blaze FHIR servers)


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
## First Steps with running the station

1. Run `docker-compose up -d`.
2. Check that the logs do not contain any startup errors with  `docker-compose logs -f`.
3. Go to `http://localhost:8080` and check whether you can see the web interface of Apache Airflow.
4. Login to the airflow web interface with the previously set user credentials


## Troubleshooting/FAQ

### Using pre-built images

If there are issues while building the airflow container you can use our prebuilt images to run the airflow instance.
Edit the airflow service in the docker-compose.yml file and replace the build command with our prebuilt image:

```yaml
# ------------- ommitted ------------
services:
  airflow:
    # remove the build command
    build: './airflow'
    # replace with the image command
    image: ghcr.io/pht-medic/station-airflow:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
# ------------- ommitted ------------
```




