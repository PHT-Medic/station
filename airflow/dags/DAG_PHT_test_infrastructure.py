from datetime import timedelta
import json
import os

import docker
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.utils.dates import days_ago
from train_lib.train.build_test_train import build_test_train
from train_lib.fhir import PHTFhirClient
from train_lib.security import SecurityProtocol

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

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
def test_station_infrastructure():
    @task()
    def test_docker():
        client = docker.from_env()
        registry_address = os.getenv("HARBOR_API_URL").split("//")[-1]

        client.login(username=os.getenv("HARBOR_USER"), password=os.getenv("HARBOR_PW"),
                     registry=registry_address)

    @task()
    def get_fhir_server_config():
        context = get_current_context()
        config = context['dag_run'].conf

        env_dict = config.get("env", None)
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

        if fhir_user and not (fhir_pw or fhir_token):
            raise ValueError(
                "Incomplete FHIR credentials, either a token or a password need to be set for a fhir user.")

        if not fhir_user and (fhir_pw or fhir_token):
            raise ValueError("Incomplete FHIR credentials, token or password set but no user given.")

        return  {
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
                                    server_type=fhir_config["FHIR_SERVER_TYPE"]
                                    )
        fhir_client.health_check()

    test_docker()
    fhir_config = get_fhir_server_config()
    test_fhir_config(fhir_config)

infrastructure_dag = test_station_infrastructure()
