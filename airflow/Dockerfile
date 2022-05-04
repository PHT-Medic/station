FROM ubuntu
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
    # install python
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y python3.8 && apt install python-is-python3 && apt install -y python3-pip && \
    rm -rf /var/lib/apt/lists


# Install container diff library
RUN curl -LO https://storage.googleapis.com/container-diff/latest/container-diff-linux-amd64 && \
    install container-diff-linux-amd64 /usr/local/bin/container-diff

# install airflow
RUN pip install "apache-airflow[celery,crypto,hashicorp,password,postgres,redis]==2.2.4" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.4/constraints-3.8.txt"

RUN mkdir /opt/train_data
COPY requirements.txt /tmp/requirements.txt


RUN pip install -r /tmp/requirements.txt


COPY airflow.cfg /root/airflow/airflow.cfg
COPY ./dags /root/airflow/dags
# install train container library

RUN pip install git+https://github.com/PHT-Medic/train-container-library.git

COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh
ENTRYPOINT ["/root/entrypoint.sh"]
CMD ["webserver"]

