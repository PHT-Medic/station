import datetime
import os

import airflow
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook

from pht_trainlib.context import TrainContext
from pht_trainlib.docker_ops import list_volumes

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

dag = airflow.DAG(dag_id='PHT_process', default_args=default_args, schedule_interval=None)


def get_container_registry():
    return BaseHook.get_connection('pht_station_all_docker_container_registry')


def get_params(context):
    p = context['params']
    return p['processing_id'], p['repository'], p['tag'], p['tracker_identity_id']


# def pull(**context):
#     """
#     Pulls the train image for extracting the meta data from it.
#     """
#     repo, tag, station_id, __ = get_params(context)
#     registry = get_container_registry()
#     pull_result = docker_ops.pull(
#         repository=registry.host + '/' + repo,
#         tag=tag)
#     return pull_result.attrs['Id']

##
# Python Operator
##


# TODO Replace with the inspection from the database
def determine_endpoint(**context):
    __, repo, tag, __ = get_params(context)
    registry = get_container_registry()
    image = registry.host + '/' + repo + ':' + tag
    with TrainContext() as tc:
        endpoint = tc.run_get_endpoint_of_currently_running_execution(image)
    return endpoint


def process(**context):
    __, repo, tag, __ = get_params(context)
    registry = get_container_registry()
    image = registry.host + '/' + repo + ':' + tag
    endpoint = context['task_instance'].xcom_pull(task_ids='PHT_process_determine_endpoint')

    # TODO Resource config
    volumes = {
            volume.name: {
                'bind': os.path.join('/', 'mnt', volume.name),
                'mode': 'ro'
            } for volume in list_volumes() if volume.name.startswith('pht')
    }

    environment = {
        'PHT_RESOURCE_' + key.upper(): value['bind'] for (key, value) in volumes.items()
    }

    with TrainContext() as tc:
        response = tc.run(
            command='',
            image=image,
            entrypoint=f'/opt/pht_train/endpoints/{endpoint}/commands/run/entrypoint.py',
            network_disabled=True,
            working_dir='/opt/pht_train/executions/_currently_running/_working',
            environment=environment,
            volumes=volumes)
        print(response, flush=True)


t1 = PythonOperator(
    python_callable=determine_endpoint,
    provide_context=True,
    task_id='PHT_process_determine_endpoint',
    dag=dag)


t2 = PythonOperator(
    python_callable=process,
    provide_context=True,
    task_id='PHT_process_process',
    dag=dag)

t1 >> t2





# TODO Backlog

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
