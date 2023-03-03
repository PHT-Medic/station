FROM python:3.10-bullseye
MAINTAINER michael.graf@uni-tuebingen.de

ENV DEBIAN_FRONTEND=noninteractive

EXPOSE 8080 5555 8793

# install python3.8 and os dependencies
RUN apt -y update && apt-get -y install software-properties-common && \
    apt-get install -yqq --no-install-recommends --no-install-suggests \
        git \
        libffi-dev \
        libpq-dev \
        build-essential \
        apt-utils \
        netcat \
        locales \
        curl && \
#    # install python
#    apt install python-is-python3 && apt install -y python3-pip && \
    rm -rf /var/lib/apt/lists

# install airflow
RUN pip install "apache-airflow[celery,crypto,hashicorp,password,postgres,redis]==2.5.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.1/constraints-3.10.txt"

RUN mkdir /opt/train_data
# COPY requirements.txt /tmp/requirements.txt


# RUN pip install -r /tmp/requirements.txt


COPY airflow.cfg /root/airflow/airflow.cfg
COPY ./dags /root/airflow/dags
# install train container library

RUN pip install --force-reinstall -v "pht-train-container-library==2.0.0a6"

COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh
ENTRYPOINT ["/root/entrypoint.sh"]
CMD ["webserver"]

