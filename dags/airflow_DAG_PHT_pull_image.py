import sys
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


def push_docker_image(**context):
    conf = ['repository', 'tag', 'cmd', 'entrypoint']
    repository, tag, cmd, entrypoint = [context['dag_run'].conf[_] for _ in conf]
    image = ':'.join([repository, tag])
    # Run container again
    client = docker.from_env()
    print(f"Running command {cmd}")
    container = client.containers.run(image=image, command=cmd, detach=True, entrypoint=entrypoint)
    # Pause running container
    print(container.logs().decode("utf-8"))
    container.wait()
    # Update recent image
    image = container.commit(tag=tag, repository=repository)
    print(image.id)
    # Login needed?
    client.login(username='boette', password='Start123!', registry='https://harbor.pht.medic.uni-tuebingen.de/harbor/sign-in')
    for line in client.images.push(repository=repository, tag=tag, stream=False, decode=False):
        print(line)


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


t3 = PythonOperator(
    task_id='push_docker_image',
    provide_context=True,
    python_callable=push_docker_image,
    execution_timeout=datetime.timedelta(minutes=1),
    dag=dag,
        )


t1 >> t2 >> t3
