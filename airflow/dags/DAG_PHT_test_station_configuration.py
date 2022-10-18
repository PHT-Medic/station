import asyncio
import os

import docker
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.utils.dates import days_ago
from train_lib.clients import PHTFhirClient
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import docker.types

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


@dag(default_args=default_args, schedule_interval=None, start_date=days_ago(2), tags=['pht', "test"])
def test_station_configuration():
    @task()
    def test_docker():
        client = docker.from_env()
        registry_address = os.getenv("HARBOR_URL").split("//")[-1]

        client.login(username=os.getenv("HARBOR_USER"), password=os.getenv("HARBOR_PW"),
                     registry=registry_address)


    @task()
    def get_dag_config():
        context = get_current_context()
        config = context['dag_run'].conf
        return config

    @task()
    def get_fhir_server_config(config):

        env_dict = config.get("env", None)
        print(env_dict)
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

        if not fhir_url:
            raise ValueError("No FHIR server specified")

        if fhir_pw and fhir_token:
            raise ValueError("Conflicting authentication information, both password and token are set.")

        if not fhir_user and fhir_pw:
            raise ValueError("Incomplete FHIR credentials, password set but no user given.")

        if not fhir_token and not (fhir_user and fhir_pw):
            print("No auth information given")
            raise ValueError("No credentials given for fhir server")

        return {
            "FHIR_ADDRESS": fhir_url,
            "FHIR_USER": fhir_user,
            "FHIR_TOKEN": fhir_token,
            "FHIR_PW": fhir_pw,
            "FHIR_SERVER_TYPE": fhir_server_type
        }

    @task()
    def test_fhir_config(fhir_config):
        print(fhir_config)
        fhir_client = PHTFhirClient(server_url=fhir_config["FHIR_ADDRESS"],
                                    password=fhir_config["FHIR_PW"],
                                    username=fhir_config["FHIR_USER"],
                                    token=fhir_config["FHIR_TOKEN"],
                                    fhir_server_type=fhir_config["FHIR_SERVER_TYPE"]
                                    )
        fhir_client.health_check()

    @task()
    def test_fhir_query(config, fhir_config):

        query_dict = config.get("query", None)
        print(query_dict)
        if query_dict:

            fhir_client = PHTFhirClient(server_url=fhir_config["FHIR_ADDRESS"],
                                        password=fhir_config["FHIR_PW"],
                                        username=fhir_config["FHIR_USER"],
                                        token=fhir_config["FHIR_TOKEN"],
                                        fhir_server_type=fhir_config["FHIR_SERVER_TYPE"],
                                        )

            fhir_client.output_format = "raw"
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(fhir_client.execute_query(query=query_dict))
            print(result)

        else:
            print("No FHIR Query provided.")

    @task()
    def test_load_private_key():
        private_key_path = os.getenv("PRIVATE_KEY_PATH")

        if not private_key_path:
            raise ValueError("No path to private key found.")

        with open(private_key_path, "rb") as private_key_file:
            private_key = load_pem_private_key(private_key_file.read(), password=None)

        print("Private key loaded successfully.")

    @task()
    def test_gpu_docker():
        smi_image = "nvidia/cuda:10.0-base-ubuntu18.04"
        client = docker.from_env()
        device_request = docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
        container = client.containers.run(
            smi_image,
            command="nvidia-smi",
            detach=True,
            device_requests=[device_request]
        )
        container.wait()
        output = container.logs()
        print(output.decode("utf-8"))
        container.remove()







    test_docker()
    dag_config = get_dag_config()
    fhir_config = get_fhir_server_config(dag_config)
    test_fhir_config(fhir_config)
    if dag_config["query"]:
        test_fhir_query(dag_config, fhir_config)
    test_load_private_key()
    test_gpu_docker()


configuration_dag = test_station_configuration()
