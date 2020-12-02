import sys
import datetime
import airflow
import docker

import configparser
import requests
import json
import os
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


dag = airflow.DAG(dag_id='extract_results', default_args=default_args, schedule_interval=None)


def pull_docker_image(**context):
    repository, tag = [context['dag_run'].conf[_] for _ in ['repository', 'tag']]
    # Pull the image.
    client = docker.from_env()
    client.images.pull(repository=repository, tag=tag)
    # Pull base image as well
    client.images.pull(repository=repository, tag='base')
    # Make sure the image with the desired tag is there.
    images = client.images.list()
    image_tags = sum([i.tags for i in images], [])
    assert(':'.join([repository, tag]) in image_tags)
    print("Image was successfully pulled.")
    assert(':'.join([repository, 'base']) in image_tags)
    print("Baseimage was successfully pulled.")
