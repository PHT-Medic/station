#!/bin/bash

set -e

if [ "$1" = 'webserver' ]; then
    airflow db init
    echo $AIRFLOW_USER
    echo $AIRFLOW_PW
    airflow users create --username $AIRFLOW_USER --firstname FIRST_NAME --lastname LAST_NAME --role Admin --email admin@station.org -p $AIRFLOW_PW
    airflow scheduler &
    exec  airflow webserver

elif [ "$1" = 'worker' ]; then
    exec  airflow worker

elif [ "$1" = 'init' ]; then
    airflow db init
    airflow users create --username admin --firstname FIRST_NAME --lastname LAST_NAME --role Admin --email admin@example.org -p admin
    airflow connections add 'station_db' --conn-type 'postgres' --conn-login 'admin' --conn-password 'admin' --conn-host 'postgres' --conn-port '5432' --conn-schema "pht_station_${STATION_ID}"
    # exec  station_airflow worker
else
    exec "$@"
fi

