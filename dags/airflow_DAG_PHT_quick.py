import datetime

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
# Python Operator
##


def get_image_from_context(context):
    return context['params']['image']


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
    print(inspection, flush=True)


t1 = PythonOperator(
    python_callable=op_pull,
    provide_context=True,
    task_id='PHT_quick_op_pull',
    dag=dag)


t2 = PythonOperator(
    python_callable=op_inspect,
    provide_context=True,
    task_id='PHT_quick_op_inspect',
    dag=dag)


t1 >> t2
