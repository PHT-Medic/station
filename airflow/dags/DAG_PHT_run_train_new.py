import asyncio
import sys
from datetime import timedelta
import json
import os

import docker
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.utils.dates import days_ago
from docker.errors import APIError
from train_lib.train.build_test_train import build_test_train
from train_lib.fhir import PHTFhirClient
from train_lib.security import SecurityProtocol
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

from train_lib.docker_util.docker_ops import extract_train_config, extract_query_json
from train_lib.security.SecurityProtocol import SecurityProtocol
from train_lib.fhir import PHTFhirClient
from train_lib.docker_util.validate_master_image import validate_train_image

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}


@dag(default_args=default_args, schedule_interval=None, start_date=days_ago(2), tags=['pht', 'train'])
def run_pht_train():
    @task()
    def get_train_image_info():
        context = get_current_context()
        repository, tag, env, volumes = [context['dag_run'].conf.get(_, None) for _ in
                                         ['repository', 'tag', 'env', 'volumes']]
        img = repository + ":" + tag

        train_state_dict = {
            "repository": repository,
            "tag": tag,
            "img": img,
            "env": env,
            "volumes": volumes
        }

        return train_state_dict

    @task()
    def pull_docker_image(train_state):
        client = docker.from_env()

        registry_address = os.getenv("HARBOR_API_URL").split("//")[-1]
        print(registry_address)
        client.login(username=os.getenv("HARBOR_USER"), password=os.getenv("HARBOR_PW"),
                     registry=registry_address)
        client.images.pull(repository=train_state["repository"], tag=train_state["tag"])

        # Pull base image as well
        client.images.pull(repository=train_state["repository"], tag='base')
        # Make sure the image with the desired tag is there.
        images = client.images.list()
        image_tags = sum([i.tags for i in images], [])
        assert (':'.join([train_state["repository"], train_state["tag"]]) in image_tags)
        print("Image was successfully pulled.")
        assert (':'.join([train_state["repository"], 'base']) in image_tags)
        print("Base image was successfully pulled.")

        return train_state

    @task()
    def extract_config_and_query(train_state):
        config = extract_train_config(train_state["img"])
        query = extract_query_json(train_state["img"])
        train_state["config"] = config
        train_state["query"] = query

        return train_state

    @task()
    def validate_against_master_image(train_state):
        master_image = train_state["config"]["master_image"]
        img = train_state["img"]
        validate_train_image(train_img=img, master_image=master_image)
        return train_state

    @task()
    def pre_run_protocol(train_state):
        config = train_state["config"]
        sp = SecurityProtocol(os.getenv("STATION_ID"), config=config)
        sp.pre_run_protocol(train_state["img"], os.getenv("PRIVATE_KEY_PATH"))

        return train_state

    @task()
    def execute_query(train_state):

        env_dict = train_state.get("env", None)
        if env_dict:
            fhir_url = env_dict.get("FHIR_ADDRESS", None)
            fhir_user = env_dict.get("FHIR_USER", None)
            fhir_pw = env_dict.get("FHIR_PW", None)
            fhir_token = env_dict.get("FHIR_TOKEN", None)
            fhir_server_type = env_dict.get("FHIR_SERVER_TYPE", None)
        else:
            fhir_url = os.getenv("FHIR_ADDRESS", None)
            fhir_user = os.getenv("FHIR_USER", None)
            fhir_pw = os.getenv("FHIR_PW", None)
            fhir_token = os.getenv("FHIR_TOKEN", None)
            fhir_server_type = os.getenv("FHIR_SERVER_TYPE", None)

        fhir_client = PHTFhirClient(
            server_url=fhir_url,
            username=fhir_user,
            password=fhir_pw,
            token=fhir_token,
            fhir_server_type=fhir_server_type
        )
        with asyncio.get_event_loop() as loop:
            result = loop.run_until_complete(fhir_client.execute_query(query=train_state["query"]))
            print(result)

        output_format = train_state["query"]["data"]["output_format"]
        output_file_name = train_state["query"]["data"]["filename"]
        # TODO get full path
        train_state["volumes"] = {output_file_name: f"opt/pht_train/data/{output_file_name}"}

        return train_state

    @task()
    def execute_container(train_state):
        client = docker.from_env()
        environment = train_state.get("env", {})
        volumes = train_state.get("volumes", {})

        container_name = f'{train_state["repository"].split("/")[-1]}.{train_state["tag"]}'
        try:
            container = client.containers.run(train_state["img"], environment=environment, volumes=volumes,
                                              name=container_name, detach=True)
        # If the container is already in use remove it
        except APIError as e:
            print(e)
            client.containers.remove(container_name)
            container = client.containers.run(train_state["img"], environment=environment, volumes=volumes,
                                              name=container_name, detach=True)

        exit_code = container.wait()["StatusCode"]
        container.commit(repository=train_state["repository"], tag=train_state["tag"])
        print(container.logs().decode("utf-8"))
        if exit_code != 0:
            raise ValueError(f"The train execution returned a non zero exit code: {exit_code}")

        return train_state

    @task()
    def post_run_protocol(train_state):
        config = train_state["config"]
        sp = SecurityProtocol(os.getenv("STATION_ID"), config=config)
        sp.post_run_protocol(img=train_state["img"], private_key_path=os.getenv("PRIVATE_KEY_PATH"))

        return train_state

    @task()
    def rebase(train_state):
        base_image = ':'.join([train_state["repository"], 'base'])
        client = docker.from_env(timeout=120)
        to_container = client.containers.create(base_image)
        updated_tag = train_state["tag"]

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

        from_container = client.containers.create(train_state["img"])

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

        print(f'Creating image: {train_state["repository"]}:{updated_tag}')
        print(type(to_container))
        # Rebase the train
        try:
            img = to_container.commit(repository=train_state["repository"], tag="base")
            # remove executed containers -> only images needed from this point
            print('Removing containers')
            to_container.remove()
            from_container.remove()
            return train_state
        except Exception as err:
            print(err)
            sys.exit()

    @task()
    def push_train_image(train_state):
        client = docker.from_env()

        registry_address = os.getenv("HARBOR_API_URL").split("//")[-1]

        client.login(username=os.getenv("HARBOR_USER"), password=os.getenv("HARBOR_PW"),
                     registry=registry_address)

        response = client.images.push(
            repository=train_state["repository"],
            tag=train_state["tag"],
            stream=False, decode=False
        )
        print(response)

    train_state = get_train_image_info()
    train_state = pull_docker_image(train_state)
    train_state = extract_config_and_query(train_state)
    train_state = validate_against_master_image(train_state)
    train_state = pre_run_protocol(train_state)
    train_state = execute_query(train_state)
    train_state = execute_container(train_state)
    train_state = post_run_protocol(train_state)
    train_state = rebase(train_state)
    push_train_image(train_state)


run_train_dag = run_pht_train()
