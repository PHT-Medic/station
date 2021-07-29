import sys
import datetime
import airflow
import docker

import requests
import json
import os

from docker.errors import APIError
from train_lib.docker_util.docker_ops import extract_train_config
from train_lib.security.SecurityProtocol import SecurityProtocol

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

dag = airflow.DAG(dag_id='run_train', default_args=default_args, schedule_interval=None)


def pull_docker_image(**context):
    repository, tag = [context['dag_run'].conf[_] for _ in ['repository', 'tag']]
    # Pull the image.
    client = docker.from_env()

    registry_address = "/".join(os.getenv("HARBOR_API_URL").split("/")[:-2])

    client.login(username=os.getenv("HARBOR_USER"), password=os.getenv("HARBOR_PW"),
                 registry=registry_address)
    client.images.pull(repository=repository, tag=tag)
    # Pull base image as well
    client.images.pull(repository=repository, tag='base')
    # Make sure the image with the desired tag is there.
    images = client.images.list()
    image_tags = sum([i.tags for i in images], [])
    assert (':'.join([repository, tag]) in image_tags)
    print("Image was successfully pulled.")
    assert (':'.join([repository, 'base']) in image_tags)
    print("Base image was successfully pulled.")


def pre_run_protocol(**context):
    repository, tag = [context['dag_run'].conf[_] for _ in ['repository', 'tag']]
    img = repository + ":" + tag
    config = extract_train_config(img)
    print(os.getenv("STATION_ID"))
    sp = SecurityProtocol(os.getenv("STATION_ID"), config=config)
    print(os.getenv("STATION_PRIVATE_KEY_PATH"))
    sp.pre_run_protocol(img=img, private_key_path=os.getenv("STATION_PRIVATE_KEY_PATH"))


def execute_container(**context):
    conf = ['repository', 'tag', 'cmd', 'entrypoint']
    repository, tag, cmd, entrypoint = [context['dag_run'].conf.get(_, None) for _ in conf]
    image = ':'.join([repository, tag])
    # create name fro the container to be able to grab the container in later tasks
    container_name = f'{repository.split("/")[-1]}.{tag}'
    client = docker.from_env()
    print(f"Running command {cmd}")
    environment = context['dag_run'].conf['env'] if 'env' in context['dag_run'].conf.keys() else {}
    volume = context['dag_run'].conf['vol'] if 'vol' in context['dag_run'].conf.keys() else {}
    print(f"Environment input for container: {environment}")
    print(f"Volume input for container: {volume}")
    if cmd and entrypoint:
        # Run container with a specified command and entrypoint
        print("Running with custom entrypoint")
        try:
            container = client.containers.run(image=image, command=cmd, detach=True, entrypoint=entrypoint,
                                              volumes=volume, environment=environment, name=container_name)

        # If the container is already in use remove it
        except APIError as e:
            print(e)
            client.containers.remove(container_name)
            container = client.containers.run(image=image, command=cmd, detach=True, entrypoint=entrypoint,
                                              volumes=volume, environment=environment, name=container_name)

    else:
        # Run container with default command and entrypoint
        print("Running with default command")
        try:
            container = client.containers.run(image, environment=environment, volumes=volume,
                                              name=container_name, detach=True)
        # If the container is already in use remove it
        except APIError as e:
            print(e)
            client.containers.remove(container_name)
            container = client.containers.run(image, environment=environment, volumes=volume,
                                              name=container_name, detach=True)

    exit_code = container.wait()["StatusCode"]
    container.commit(repository=repository, tag=tag)
    print(container.logs().decode("utf-8"))
    if exit_code != 0:
        print(f"The command {cmd} resulted in a non-zero exit code: {exit_code}")
        sys.exit()


def post_run_protocol(**context):
    repository, tag = [context['dag_run'].conf[_] for _ in ['repository', 'tag']]
    img = repository + ":" + tag
    config = extract_train_config(img)
    sp = SecurityProtocol(os.getenv("STATION_ID"), config=config)
    sp.post_run_protocol(img=img, private_key_path=os.getenv("STATION_PRIVATE_KEY_PATH"))


def rebase(**context):
    repository, tag = [context['dag_run'].conf[_] for _ in ['repository', 'tag']]
    # Build container name from context to get executed container
    # container_name = f'{repository.split("/")[-1]}.{tag}'
    base_image = ':'.join([repository, 'base'])
    client = docker.from_env(timeout=120)
    # Grab the base image to rebase the train, only adds one layer in total and not one per station
    to_container = client.containers.create(base_image)
    updated_tag = tag

    # TODO only copy the results directory + train_config.json

    def _copy(from_cont, from_path, to_cont, to_path):
        """
        Copies a file from one container to another container
        :param from_cont:
        :param from_path:
        :param to_cont:
        :param to_path:
        :return:
        """
        tar_stream, _ = from_cont.get_archive(from_path)
        to_cont.put_archive(os.path.dirname(to_path), tar_stream)

    from_container = client.containers.create(f"{repository}:latest")

    # Copy results to base image
    _copy(from_cont=from_container,
          from_path="/opt/pht_results",
          to_cont=to_container,
          to_path="/opt/pht_results")

    # Hardcoded copying of train_config.json
    _copy(from_cont=from_container,
          from_path="/opt/train_config.json",
          to_cont=to_container,
          to_path="/opt/train_config.json")

    print('Copied files into baseimage')

    print(f'Creating image: {repository}:{updated_tag}')
    print(type(to_container))
    # Rebase the train
    try:
        img = to_container.commit(repository=repository, tag="base")
        # remove executed containers -> only images needed from this point
        print('Removing containers')
        to_container.remove()
        from_container.remove()
    except Exception as err:
        print(err)
        sys.exit()


def push_docker_image(**context):
    conf = ['repository', 'tag']
    repository, tag = [context['dag_run'].conf[_] for _ in conf]
    # Run container again
    client = docker.from_env()
    # Login needed?
    registry_address = "/".join(os.getenv("HARBOR_API_URL").split("/")[:-2])
    client.login(username=os.getenv("HARBOR_USER"), password=os.getenv("HARBOR_PW"),
                 registry=registry_address)
    response = client.images.push(repository=repository, tag=tag, stream=False, decode=False)
    print(response)


t1 = PythonOperator(
    task_id='pull_docker_image',
    provide_context=True,
    python_callable=pull_docker_image,
    dag=dag,
)

t2 = PythonOperator(
    task_id="pre-run_protocol",
    provide_context=True,
    python_callable=pre_run_protocol,
    execution_timeout=datetime.timedelta(minutes=5),
    dag=dag
)

t3 = PythonOperator(
    task_id='execute_container',
    provide_context=True,
    python_callable=execute_container,
    execution_timeout=datetime.timedelta(minutes=1),
    dag=dag,
)

t4 = PythonOperator(
    task_id="post-run_protocol",
    provide_context=True,
    python_callable=post_run_protocol,
    execution_timeout=datetime.timedelta(minutes=5),
    dag=dag
)

t5 = PythonOperator(
    task_id='rebase',
    provide_context=True,
    python_callable=rebase,
    execution_timeout=datetime.timedelta(minutes=5),
    dag=dag,
)

t6 = PythonOperator(
    task_id='push_docker_image',
    provide_context=True,
    python_callable=push_docker_image,
    execution_timeout=datetime.timedelta(minutes=1),
    dag=dag,
)


t1 >> t2 >> t3 >> t4 >> t5 >> t6