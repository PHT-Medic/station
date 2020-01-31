import datetime

import airflow
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook

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


def get_params(context):
    params = context['params']
    return params['repository'], params['tag'], params['station_id'], params['tracker_id']


def get_container_registry():
    return BaseHook.get_connection('pht_station_all_docker_container_registry')


def get_tracker(station_id, tracker_id):
    conn = BaseHook.get_connection(f'pht_station_{station_id}_http_station_api')
    host, port, schema = conn.host, conn.port, conn.schema



##
# Python Operator
##

def pull(**context):
    """
    Pulls the train image for extracting the meta data from it.
    """
    repo, tag, station_id, __ = get_params(context)
    registry = get_container_registry()
    pull_result = docker_ops.pull(
        repository=registry.host + '/' + repo,
        tag=tag)
    return pull_result.attrs['Id']


def verify_fs_layer(**context):
    """
    Verifies that the FSLayers of the pulled image are the one expected using the tracker
    """
    image_id = context['task_instance'].xcom_pull(task_ids='pull')
    __, __, station_id, tracker_id = get_params(context)
    tracker = get_tracker(station_id, tracker_id)


    # print(image_id, flush=True)
    # print(tracker_id, flush=True)
    # print('-------------------------------------------------------------------------', flush=True)


t1 = PythonOperator(
    python_callable=pull,
    provide_context=True,
    task_id='pull',
    dag=dag)

t2 = PythonOperator(
    python_callable=verify_fs_layer,
    provide_context=True,
    task_id='verify_fs_layer',
    dag=dag)

t1 >> t2
