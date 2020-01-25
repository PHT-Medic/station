"""
This is a DAG which just fails. Used for testing.
"""
import datetime

import airflow
from airflow.operators.python_operator import PythonOperator

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

dag = airflow.DAG(dag_id='test_fail', default_args=default_args, schedule_interval=None)


def _fail(**kwargs):
    raise AssertionError('This is supposed to happen!')


PythonOperator(
    python_callable=_fail,
    provide_context=True,
    task_id='_fail',
    dag=dag)
