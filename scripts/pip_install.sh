#!/usr/bin/env sh
set -eu
pip install --upgrade --extra-index-url 'https://pypiserver.lukaszimmermann.dev' --no-cache-dir \
	'apache-airflow[celery,crypto,password]' \
       	pht-trainlib \
	psycopg2 \

