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

dag = airflow.DAG('inspect_endpoints', default_args=default_args, schedule_interval=None)


def _pull(**kwargs):
    # TODO Figure out where the client should be retrieved from
    print('hello world', flush=True)
    print(kwargs, flush=True)
    print('end of world', flush=True)
    # docker_ops.pull(
    #     client=docker.from_env(),
    #     repository=kwargs['repository'],
    #     tag=kwargs['tag'])


PythonOperator(
    python_callable=_pull,
    provide_context=True,
    task_id='pull_image',
    dag=dag)
