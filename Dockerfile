FROM python:3.7.7-slim-buster AS airflow_base

EXPOSE 8080 5555 8793
SHELL [ "/bin/bash", "-euo", "pipefail", "-c" ]

ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow
ENV AIRFLOW_USER_HOME=/usr/local/airflow
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}

# For PHT
ENV PHT_STATION_AIRFLOW_STATIC=/usr/local/lib/python3.7/site-packages/airflow/www/static

# Define locales
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

COPY requirements.txt /tmp/
RUN apt-get update -yqq \
    && apt-get dist-upgrade -yqq \
    && apt-get install -yqq --no-install-recommends --no-install-suggests \
        git \
        libffi-dev \
        libpq-dev \
        build-essential \
        apt-utils \
        netcat \
        locales \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && pip install --compile --no-cache-dir -r /tmp/requirements.txt \
    # Make some Airflow static assets available to the PHT Station plugin
    && mkdir -p ${AIRFLOW_USER_HOME}/plugins/static/ \
    && cp ${PHT_STATION_AIRFLOW_STATIC}/sort_both.png \
          ${AIRFLOW_USER_HOME}/plugins/static/ \
    && cp ${PHT_STATION_AIRFLOW_STATIC}/sort_asc.png \
          ${AIRFLOW_USER_HOME}/plugins/static/ \
    && cp ${PHT_STATION_AIRFLOW_STATIC}/sort_desc.png \
          ${AIRFLOW_USER_HOME}/plugins/static/ \
    && pip install git+https://gitlab.com/PersonalHealthTrain/implementations/germanmii/difuture/train-container-library.git \
    # Image cleanup
    && apt-get purge --auto-remove -yqq \
        build-essential \
        git \
    && apt-get autoremove -yqq --purge \
    && apt-get -yqq clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base && sync

FROM airflow_base

COPY www/static/select.dataTables.min.css www/static/dataTables.select.min.js ${PHT_STATION_AIRFLOW_STATIC}/
COPY www/templates ${AIRFLOW_USER_HOME}/plugins/templates

COPY scripts/entrypoint.sh scripts/airflow_setup.py ${AIRFLOW_USER_HOME}/bin/
COPY config/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg
COPY dags ${AIRFLOW_USER_HOME}/dags

WORKDIR ${AIRFLOW_USER_HOME}
ENTRYPOINT ["/usr/local/airflow/bin/entrypoint.sh"]
CMD ["webserver"]
