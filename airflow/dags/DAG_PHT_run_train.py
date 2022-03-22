import sys
import os
import os.path

import docker
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

from docker.errors import APIError

from airflow.utils.dates import days_ago

from train_lib.docker_util.docker_ops import extract_train_config, extract_query_json
from train_lib.security.protocol import SecurityProtocol
from train_lib.clients import PHTFhirClient
from train_lib.docker_util.validate_master_image import validate_train_image
from train_lib.security.train_config import TrainConfig

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

        if not tag:
            tag = "latest"
        img = repository + ":" + tag

        # check an process the volumes passed to the dag via the config
        if volumes:
            assert isinstance(volumes, dict)
            # if a volume in the dictionary follows the docker format pass it as is

            for key, item in volumes.items():
                # check if docker volume keys are present and raise an error if not
                if isinstance(item, dict):
                    if not ("bind" in item and "mode" in item):
                        raise ValueError("Incorrectly formatted docker volume, 'bind' and 'mode' keys are required")
                # transform simple path:path volumes into correctly formatted docker read only volumes
                elif isinstance(item, str):
                    volumes[key] = {
                        "bind": item,
                        "mode": "ro"
                    }

        train_id = repository.split("/")[-1]
        train_state_dict = {
            "train_id": train_id,
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
        train_state["config"] = config.dict(by_alias=True)

        # try to extract th query json if it exists under the specified path
        try:
            query = extract_query_json(train_state["img"])
            train_state["query"] = query
        except Exception as e:
            print(e)
            train_state["query"] = None
            print("No query file found ")

        return train_state

    # @task()
    # def validate_against_master_image(train_state):
    #     master_image = train_state["config"]["master_image"]
    #     img = train_state["img"]
    #     validate_train_image(train_img=img, master_image=master_image)
    #     return train_state

    @task()
    def pre_run_protocol(train_state):
        config = TrainConfig(**train_state["config"])
        sp = SecurityProtocol(os.getenv("STATION_ID"), config=config)
        sp.pre_run_protocol(train_state["img"], os.getenv("PRIVATE_KEY_PATH"))

        return train_state

    @task()
    def execute_query(train_state):
        print(train_state)
        query = train_state.get("query", None)
        if query:
            print("Query found, setting up connection to FHIR server")

            env_dict = train_state.get("env", None)
            if env_dict:
                fhir_url = env_dict.get("FHIR_ADDRESS", None)
                # Check that there is a FHIR server specified in the configuration dictionary
                if fhir_url:
                    fhir_client = PHTFhirClient.from_dict(env_dict)

                else:
                    fhir_client = PHTFhirClient.from_env()
            else:
                fhir_client = PHTFhirClient.from_env()

            query_result = fhir_client.execute_query(query=train_state["query"])

            output_file_name = query["data"]["filename"]

            # Create the file path in which to store the FHIR query results
            data_dir = os.getenv("AIRFLOW_DATA_DIR", "/opt/station_data")
            train_data_dir = os.path.join(data_dir, train_state["train_id"])

            if not os.path.isdir(train_data_dir):
                os.mkdir(train_data_dir)

            train_data_dir = os.path.abspath(train_data_dir)
            print("train data dir: ", train_data_dir)

            train_data_path = fhir_client.store_query_results(query_result, storage_dir=train_data_dir,
                                                              filename=output_file_name)
            print("train data path: ", train_data_path)
            host_data_path = os.path.join(os.getenv("STATION_DATA_DIR"), train_state["train_id"], output_file_name)

            # Add the file containing the fhir query results to the volumes configuration
            query_data_volume = {
                host_data_path: {
                    "bind": f"/opt/train_data/{output_file_name}",
                    "mode": "ro"
                }
            }

            data_dir_env = {
                "TRAIN_DATA_PATH": f"/opt/train_data/{output_file_name}"
            }

            if isinstance(train_state.get("volumes"), dict):
                train_state["volumes"] = {**query_data_volume, **train_state["volumes"]}
            else:
                train_state["volumes"] = query_data_volume

            if train_state.get("env", None):
                train_state["env"] = {**train_state["env"], **data_dir_env}
            else:
                train_state["env"] = data_dir_env
        return train_state

    @task()
    def execute_container(train_state):
        client = docker.from_env()
        environment = train_state.get("env", {})
        volumes = train_state.get("volumes", {})
        print("Volumes", train_state["volumes"])
        print("Env dict: ", environment)

        try:
            print("Running image", train_state["img"])
            container = client.containers.run(train_state["img"], environment=environment, volumes=volumes,
                                              detach=True, network_disabled=True, stderr=True, stdout=True)
        # If the container is already in use remove it
        except APIError as e:
            print(e)
            container = client.containers.run(train_state["img"], environment=environment, volumes=volumes,
                                              detach=True, network_disabled=True, stderr=True, stdout=True)
        container_output = container.wait()
        # Print The logs generated from std out und err out during the container run
        logs = container.logs().decode("utf-8")
        print(f"logs_container_start({logs})logs_end")
        exit_code = container_output["StatusCode"]

        if exit_code != 0:
            print(container_output)
            raise ValueError(f"The train execution returned a non zero exit code: {exit_code}")

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

        base_image = ':'.join([train_state["repository"], 'base'])
        to_container = client.containers.create(base_image)
        # Copy results to base image
        _copy(from_cont=container,
              from_path="/opt/pht_results",
              to_cont=to_container,
              to_path="/opt/pht_results")

        to_container.commit(repository=train_state["repository"], tag=train_state["tag"])
        container.remove(v=True, force=True)
        if exit_code != 0:
            raise ValueError(f"The train execution returned a non zero exit code: {exit_code}")

        return train_state

    @task()
    def post_run_protocol(train_state):

        config = TrainConfig(**train_state["config"])
        sp = SecurityProtocol(os.getenv("STATION_ID"), config=config)
        sp.post_run_protocol(img=train_state["img"],
                             private_key_path=os.getenv("PRIVATE_KEY_PATH"))

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
            img = to_container.commit(repository=train_state["repository"], tag=train_state["tag"])
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
        client.images.remove(f'{train_state["repository"]}:{train_state["tag"]}', noprune=False, force=True)
        client.images.remove(f'{train_state["repository"]}:base', noprune=False, force=True)

    train_state = get_train_image_info()
    train_state = pull_docker_image(train_state)
    train_state = extract_config_and_query(train_state)
    # train_state = validate_against_master_image(train_state)
    train_state = pre_run_protocol(train_state)
    train_state = execute_query(train_state)
    train_state = execute_container(train_state)
    train_state = post_run_protocol(train_state)
    train_state = rebase(train_state)
    push_train_image(train_state)


run_train_dag = run_pht_train()
