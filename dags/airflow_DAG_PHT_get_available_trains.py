import datetime
import airflow
import requests
import os
from pprint import pprint

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

dag = airflow.DAG(dag_id='get_trains', default_args=default_args, schedule_interval=None)


def get_available_trains_for_station(**context):
    station_id = int(os.getenv("STATION_ID"))

    endpoint = f"/projects/station_{station_id}/repositories"
    url = os.getenv("HARBOR_API_URL") + endpoint
    print(url)
    r = requests.get(url, auth=(os.getenv("HARBOR_USER"), os.getenv("HARBOR_PW")))
    pprint(r.json())
    r.raise_for_status()


t1 = PythonOperator(
    task_id='query_harbor_for_trains',
    provide_context=True,
    python_callable=get_available_trains_for_station,
    dag=dag,
)

t1
