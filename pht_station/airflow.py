from airflow.api.common.experimental.trigger_dag import trigger_dag
from airflow.hooks.base_hook import BaseHook


def trigger(dag_id, conf=None):
    return trigger_dag(dag_id=dag_id, conf=conf)


def get_container_registry_host():
    return BaseHook.get_connection('pht_station_all_docker_container_registry').host


# N.B. Keep these IDs in sync with the names in the DAG definition.
DAG_INSPECT = 'PHT_inspect'
DAG_PROCESS = 'PHT_process'
DAG_QUICK = 'PHT_quick'
