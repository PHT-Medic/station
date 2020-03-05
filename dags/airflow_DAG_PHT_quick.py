import datetime
import json
import os

import airflow
from airflow.operators.python_operator import PythonOperator

import pht_trainlib.docker_ops as docker_ops
import pht_trainlib.util as util
from pht_trainlib.context import TrainContext

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

dag = airflow.DAG(dag_id='PHT_quick', default_args=default_args, schedule_interval=None)


##
# Helper
##

def get_endpoint_from_inspection(inspection):
    endpoints = [
        execution['endpoint'] for execution in inspection['executions'] if execution['name'] == '_currently_running'
    ]
    if len(endpoints) != 1:
        raise ValueError('Invalid execution')
    return endpoints[0]


def get_volumes():
    volume_names = frozenset(volume.name for volume in docker_ops.list_volumes())
    _volume_name = 'pht_station_quick_execution'
    if _volume_name in volume_names:
        return {
            _volume_name: {
                'bind': os.path.join('/', 'data'),
                'mode': 'ro'
            }
        }


def get_image_from_context(context):
    return context['params']['image']


##
# Python Operator
##

def op_pull(**context):
    image = get_image_from_context(context)
    repo, tag = util.split_tag(image)
    docker_ops.pull(
        repository=repo,
        tag=tag)


def op_inspect(**context):
    image = get_image_from_context(context)
    with TrainContext() as train_context:
        inspection = train_context.run_inspect(image)
    return inspection


def op_process(**context):
    inspection = json.loads(context['task_instance'].xcom_pull(task_ids='PHT_quick_op_inspect'))
    endpoint = get_endpoint_from_inspection(inspection)
    with TrainContext() as tc:
        response = tc.run(
            command='',
            image=get_image_from_context(context),
            entrypoint=f'/opt/pht_train/endpoints/{endpoint}/commands/run/entrypoint.py',
            network_disabled=True,
            working_dir='/opt/pht_train/executions/_currently_running/_working',
            volumes=get_volumes())
    return response.container_id


def op_commit_and_push(**context):
    container_id = context['task_instance'].xcom_pull(task_ids='PHT_quick_op_process')
    image = get_image_from_context(context)
    repo, tag = util.split_tag(image)
    tag_new = tag + '-quick'
    docker_ops.commit(
        container_id=container_id,
        repo=repo,
        tag=tag_new)
    docker_ops.push(
        repository=repo,
        tag=tag_new)


def _op(task_id, f):
    return PythonOperator(
        python_callable=f,
        provide_context=True,
        task_id=task_id,
        dag=dag)


_op(task_id='PHT_quick_op_pull', f=op_pull) >> \
    _op(task_id='PHT_quick_op_inspect', f=op_inspect) >> \
    _op('PHT_quick_op_process', f=op_process) >> \
    _op('PHT_quick_op_commit_and_push', f=op_commit_and_push)
