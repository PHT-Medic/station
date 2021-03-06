#!/usr/bin/env python
import json

import airflow
import airflow.utils.db
from airflow import models
from airflow.contrib.auth.backends.password_auth import PasswordUser
import os
from dotenv import load_dotenv, find_dotenv


#
# def _get_station_ids_to_create() -> typing.Iterable[int]:
#
#     station_id_regex = re.compile('^[1-9][0-9]*$')
#     pht_station_prefix = 'PHT_STATION'
#
#     station_keys = [key for key in os.environ.keys() if key.startswith(pht_station_prefix)]
#     result = set()
#     for station_key in station_keys:
#         _id = station_key.split('_')[2]
#         if not station_id_regex.fullmatch(_id):
#             raise ValueError(f'Not a valid Station ID: {_id}')
#         result.add(int(_id))
#     return sorted(result)


def drop_all_connections(session):
    connections = session.query(airflow.models.Connection).all()
    for conn in connections:
        session.delete(conn)


def create_connections(session):
    conn_type_postgres = 'postgres'

    # The container registry for pulling images
    container_registry = airflow.models.Connection(
        conn_id=f'pht_station_{os.getenv("STATION_ID")}_harbor',
        conn_type='docker',
        host='harbor.personalhealthtrain.de',
        login=os.getenv("HARBOR_USER"),
        password=os.getenv("HARBOR_PW"),
        schema='https')

    # Postgres database for the Station
    postgres_station = airflow.models.Connection(
        conn_id=f'pht_station_all_{conn_type_postgres}_station_db',
        conn_type=conn_type_postgres,
        host='localhost',  # TODO change this back to db
        port=5432,
        login='station',
        schema='station',  # Maps to Database in Postgres
        password='station')
    session.add_all([
        container_registry,
        postgres_station
    ])


def create_user(session):

    if not session.query(models.User).filter(models.User.username == os.getenv("AIRFLOW_USER", "admin")).first():
        user = PasswordUser(models.User())
        user.username = os.getenv("AIRFLOW_USER", "admin")
        user.email = 'user@example.com'
        user.password = os.getenv("AIRFLOW_PW", "admin")
        session.add(user)
        session.commit()


@airflow.utils.db.provide_session
def setup_airflow(session=None):
    drop_all_connections(session)
    create_connections(session)
    create_user(session)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    setup_airflow()
