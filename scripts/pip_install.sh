#!/usr/bin/env sh
set -eu
pip install --upgrade --extra-index-url 'https://pypiserver.lukaszimmermann.dev' --no-cache-dir \
	'apache-airflow[celery,crypto,password]' \
       	pht-trainlib \
       	'marshmallow==2.19.5' \
	psycopg2 \
        'kombu<4.7,>=4.6.7'

