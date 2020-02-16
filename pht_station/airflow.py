from airflow.api.common.experimental.trigger_dag import trigger_dag


def trigger(dag_id, conf=None):
    return trigger_dag(dag_id=dag_id, conf=conf)


# N.B. Keep these IDs in sync with
DAG_INSPECT = 'PHT_inspect'
DAG_PROCESS = 'PHT_process'
