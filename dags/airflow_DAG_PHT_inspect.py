import datetime

import airflow
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook
import docker


import pht_trainlib.docker_ops as docker_ops


# start date:  datetime.datetime(2015, 6, 1)

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

dag = airflow.DAG(dag_id='inspect', default_args=default_args, schedule_interval=None)


def get_docker_connection(station_id):
    return BaseHook.get_connection(f'pht_station_{station_id}_container_registry_docker')


def _pull(**context):
    """
    Pulls the train image for extracting the meta data from it.
    """
    params = context['params']
    repo = params['repository']
    tag = params['tag']
    station_id = params['station_id']
    cr = get_docker_connection(station_id)
    image = cr.host + '/' + repo
    print(f'Repository: {repo}', flush=True)
    pull_result = docker_ops.pull(
        client=docker.from_env(),
        repository=image,
        tag=tag)
    print(f'pull_result: {pull_result}', flush=True)


PythonOperator(
    python_callable=_pull,
    provide_context=True,
    task_id='pull_image',
    dag=dag)
