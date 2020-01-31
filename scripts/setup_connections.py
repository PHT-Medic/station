#!/usr/bin/env python
import airflow
import airflow.utils.db

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
    conn_type_docker = 'docker'
    conn_type_http = 'http'

    # The container registry for pulling images
    container_registry = airflow.models.Connection(
        conn_id=f'pht_station_all_{conn_type_docker}_container_registry',
        conn_type=conn_type_docker,
        host='harbor.lukaszimmermann.dev',
        login='foo',
        password='bar',
        schema='https')

    station_api = airflow.models.Connection(
        conn_id=f'pht_station_1_{conn_type_http}_station_api',
        conn_type=conn_type_http,
        host='nginx',
        port=80,
        login='foo',
        password='bar',
        schema='http')
    session.add_all([container_registry, station_api])


@airflow.utils.db.provide_session
def setup_connections(session=None):
    drop_all_connections(session)
    create_connections(session)


if __name__ == '__main__':
    setup_connections()
