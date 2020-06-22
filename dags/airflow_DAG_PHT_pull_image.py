import datetime
import airflow
import docker

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

def pull_docker_image(**kwargs):
    try:
        repository = kwargs['dag_run'].conf['repository']  # 'harbor.pht.medic.uni-tuebingen.de/library/busybox'
        tag = kwargs['dag_run'].conf['tag']  # 'latest'
        # Pull the image.
        client = docker.from_env()
        client.images.pull(repository=repository, tag=tag)
        # Make sure the image with the desired tag is there.
        images = client.images.list()
        image_tags = sum([i.tags for i in images], [])
        assert(':'.join([repository, tag]) in image_tags)
        ret = "Image was successfully pulled."
    except:
        ret = "{} failed".format(pull_docker_image.__name__)
    return ret

t1 = PythonOperator(
    task_id='pull_docker_image',
    provide_context=True,
    python_callable=pull_docker_image,
    dag=dag,
)
