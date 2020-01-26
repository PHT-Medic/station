FROM python:3.7.6-slim-buster

SHELL [ "/bin/bash", "-euo", "pipefail", "-c" ]

ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow
ENV AIRFLOW_USER_HOME=/usr/local/airflow
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}

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
        libpq-dev \
        build-essential \
        apt-utils \
        netcat \
        locales \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && apt-get purge --auto-remove -yqq \
        build-essential \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base && sync
COPY dags ${AIRFLOW_USER_HOME}/dags
COPY app.py /usr/local/
COPY scripts/entrypoint.sh /entrypoint.sh
COPY config/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg

EXPOSE 4000 8080 5555 8793

WORKDIR ${AIRFLOW_USER_HOME}
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]
