import datetime
import json
import typing

import airflow
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook

import requests

import pht_trainlib.docker_ops as docker_ops
from pht_trainlib.context import TrainContext

from pht_station.models import TrackerIdentity


default_args = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'schedule_interval': None,  # So the DAG is not scheduled automatically
    'start_date': datetime.datetime(2019, 12, 30),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = airflow.DAG(dag_id='PHT_inspect', default_args=default_args, schedule_interval=None)


def get_container_registry():
    return BaseHook.get_connection('pht_station_all_docker_container_registry')


def get_fslayers_digests(station_id, tracker_id) -> typing.Sequence[str]:
    """
    Queries the Station API server with ID ``station_id`` for the fslayers of
    tracker with ID ``tracker_id``
    """
    c = BaseHook.get_connection(f'pht_station_{station_id}_http_station_api')
    response = requests.get(f'{c.schema}://{c.host}:{c.port}/tracker/{tracker_id}')
    if response.status_code != 200:
        raise ValueError(f'Unexpected response from Station API: {vars(response)}')
    fslayers = response.json()['fslayers']
    return [
        fslayer['digest'] for fslayer in fslayers
    ]


def get_params(context):
    params = context['params']
    return params['repository'], params['tag'], params['tracker_identity_id']


##
# Python Operator
##

def pull(**context):
    """
    Pulls the train image for extracting the meta data fr2om it.
    """
    repo, tag, __ = get_params(context)
    registry = get_container_registry()
    docker_ops.pull(repository=registry.host + '/' + repo, tag=tag)


def inspect(**context):
    """
    Pulls the train image for extracting the meta data from it.
    """
    repo, tag, tracker_identity_id = get_params(context)
    registry = get_container_registry()
    image = registry.host + '/' + repo + ':' + tag
    with TrainContext() as train_context:
        inspection = train_context.run_inspect(image)

    TrackerIdentity.update_data(tracker_identity_id=tracker_identity_id, data={
        'inspection': json.loads(inspection)
    })

# TODO
# def verify_fs_layer(**context):
#     """
#     Verifies that the FSLayers of the pulled image are the one expected using the tracker
#     """
#     image_id = context['task_instance'].xcom_pull(task_ids='pull')
#     __, __, station_id, tracker_id = get_params(context)
#
#     digests_station_api = get_fslayers_digests(station_id, tracker_id)
#     digests_docker_host = docker_ops.get_fslayers(image_id)
#     print(digests_station_api, flush=True)
#     print(digests_docker_host, flush=True)


t1 = PythonOperator(
    python_callable=pull,
    provide_context=True,
    task_id='PHT_inspect_pull',
    dag=dag)

t2 = PythonOperator(
    python_callable=inspect,
    provide_context=True,
    task_id='PHT_inspect_inspect',
    dag=dag)

t1 >> t2
