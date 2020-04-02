"""
Contains functions which interact with the Airflow Data Model
"""
import typing

from airflow.api.common.experimental.trigger_dag import trigger_dag as airflow_trigger_dag
from airflow.hooks.base_hook import BaseHook
from airflow.models import Variable


def trigger_dag(dag_id, conf=None):
    return airflow_trigger_dag(dag_id=dag_id, conf=conf)


def get_container_registry_host() -> str:
    return BaseHook.get_connection('pht_station_all_docker_container_registry').host


def get_database_connection_string() -> str:
    conn = BaseHook.get_connection('pht_station_all_postgres_station_db')
    return f'postgresql+psycopg2://{conn.login}:{conn.password}@{conn.host}/{conn.schema}'


def get_trusted_tags() -> typing.Iterable[str]:
    return [
        tag.strip() for tag in Variable.get('pht_station_all_docker_image_tags_trusted').split(',')
    ]


# N.B. Keep these IDs in sync with the names in the DAG definition.
DAG_INSPECT = 'PHT_inspect'
DAG_PROCESS = 'PHT_process'
DAG_QUICK = 'PHT_quick'
