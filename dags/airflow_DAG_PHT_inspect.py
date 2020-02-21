import datetime
import json

import airflow
from airflow.operators.python_operator import PythonOperator

import pht_trainlib.docker_ops as docker_ops
from pht_trainlib.context import TrainContext

from pht_station.dag_ops import create_image_name, get_tracker_identity_id, set_inspection


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


##
# Python Operators, in the order of execution
##

def pull(**context):
    """
    Pulls the train image for extracting the meta data fr2om it.
    """
    repo_without_tag, __, tag = create_image_name(context)
    docker_ops.pull(repository=repo_without_tag, tag=tag)


# TODO Implement me
def verify_fs_layers(**context):
    pass


def inspect(**context):
    """
    Pulls the train image for extracting the meta data from it.
    """
    __, __, image = create_image_name(context)
    tii = get_tracker_identity_id(context)

    with TrainContext() as train_context:
        inspection = train_context.run_inspect(image)

    set_inspection(tii, inspection)


t1 = PythonOperator(
    python_callable=pull,
    provide_context=True,
    task_id='PHT_inspect_pull',
    dag=dag)

t2 = PythonOperator(
    python_callable=verify_fs_layers,
    provide_context=True,
    task_id='PHT_inspect_verify_fs_layers',
    dag=dag)


t3 = PythonOperator(
    python_callable=inspect,
    provide_context=True,
    task_id='PHT_inspect_inspect',
    dag=dag)

t1 >> t2 >> t3


# TODO Backlog
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


#
# def get_fslayers_digests(station_id, tracker_id) -> typing.Sequence[str]:
#     """
#     Queries the Station API server with ID ``station_id`` for the fslayers of
#     tracker with ID ``tracker_id``
#     """
#     c = BaseHook.get_connection(f'pht_station_{station_id}_http_station_api')
#     response = requests.get(f'{c.schema}://{c.host}:{c.port}/tracker/{tracker_id}')
#     if response.status_code != 200:
#         raise ValueError(f'Unexpected response from Station API: {vars(response)}')
#     fslayers = response.json()['fslayers']
#     return [
#         fslayer['digest'] for fslayer in fslayers
#     ]
