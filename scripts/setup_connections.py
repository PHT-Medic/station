#!/usr/bin/env python
import json

import airflow
import airflow.utils.db
import os


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
        host='db',
        port=5432,
        login='station',
        schema='station',    # Maps to Database in Postgres
        password='station')
    session.add_all([
        container_registry,
        postgres_station
    ])


@airflow.utils.db.provide_session
def setup_connections(session=None):
    drop_all_connections(session)
    create_connections(session)


if __name__ == '__main__':
    setup_connections()
