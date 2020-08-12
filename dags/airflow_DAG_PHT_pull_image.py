import sys
import datetime
import airflow
import docker

# TODO: Temporary solution! As mentioned by Lukas no use of primitives like requests.
import configparser
import requests
import json

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
}


dag = airflow.DAG(dag_id='pull_image', default_args=default_args, schedule_interval=None)


def pull_docker_image(**context):
    repository, tag = [context['dag_run'].conf[_] for _ in ['repository', 'tag']]
    # Pull the image.
    client = docker.from_env()
    client.images.pull(repository=repository, tag=tag)
    # Make sure the image with the desired tag is there.
    images = client.images.list()
    image_tags = sum([i.tags for i in images], [])
    assert(':'.join([repository, tag]) in image_tags)
    print("Image was successfully pulled.")


def execute_container(**context):
    conf = ['repository', 'tag', 'cmd', 'entrypoint']
    repository, tag, cmd, entrypoint = [context['dag_run'].conf[_] for _ in conf]
    image = ':'.join([repository, tag])
    client = docker.from_env()
    print(f"Running command {cmd}")
    container = client.containers.run(image=image, command=cmd, detach=True, entrypoint=entrypoint)
    print(container.logs().decode("utf-8"))
    exit_code = container.wait()["StatusCode"]
    if exit_code != 0:
        print(f"The command {cmd} resulted in a non-zero exit code: {exit_code}")
        sys.exit()


def put_harbor_label(**context):
    # TODO integrate code, see:
    # https://redmine.medic.uni-tuebingen.de/issues/1733
    # Assumption that project name and project_repository can be extracted from the repository path from the last two labels
    repository, tag = [context['dag_run'].conf[_] for _ in ['repository', 'tag']]
    project, project_repo = repository.split('/')[-2:]
    config = configparser.ConfigParser()
    config.read(context['dag_run'].conf['conf'])
    conf = ['API_URL', 'USERNAME', 'PASSWORD']
    try:
        api, username, password = [config["credentials"][_] for _ in conf]
    except Exception as err:
        print(err)
        sys.exit()
    # Label being set currently hardcoded
    data = {'id': 7}  # pht_next id
    #data = {'id': 8}  # pht_terminate id
    print(f'Label to be added: {data}')
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    url = f'{api}/projects/{project}/repositories/{project_repo}/artifacts/{tag}/labels'
    print(f'Url for adding the label: {url}')
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data),
                                 auth=(username, password))
        response.raise_for_status()
        return "Label is added"
    except requests.exceptions.HTTPError as e:
        print(e.response.text)
        sys.exit()
    except Exception as err:
        print(err)
        sys.exit()


t1 = PythonOperator(
    task_id='pull_docker_image',
    provide_context=True,
    python_callable=pull_docker_image,
    dag=dag,
)


t2 = PythonOperator(
    task_id='execute_container',
    provide_context=True,
    python_callable=execute_container,
    execution_timeout=datetime.timedelta(minutes=1),
    dag=dag,
)


t4 = PythonOperator(
    task_id='put_harbor_label',
    provide_context=True,
    python_callable=put_harbor_label,
    execution_timeout=datetime.timedelta(minutes=1),
    dag=dag,
        )


t1 >> t2       >> t4
