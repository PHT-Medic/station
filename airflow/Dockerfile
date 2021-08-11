FROM python:3.8

EXPOSE 8080 5555 8793

RUN apt-get update -yqq \
    && apt-get dist-upgrade -yqq \
    && apt-get install -yqq --no-install-recommends --no-install-suggests \
        git \
        libffi-dev \
        libpq-dev \
        build-essential \
        apt-utils \
        netcat \
        locales
# Install container diff library
RUN curl -LO https://storage.googleapis.com/container-diff/latest/container-diff-linux-amd64 && \
    install container-diff-linux-amd64 /usr/local/bin/container-diff



COPY requirements.txt /tmp/requirements.txt


RUN pip install -r /tmp/requirements.txt
RUN pip install git+https://gitlab.com/PersonalHealthTrain/implementations/germanmii/difuture/train-container-library.git

COPY airflow.cfg /root/airflow/airflow.cfg
COPY ./dags /root/airflow/dags
COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh
ENTRYPOINT ["/root/entrypoint.sh"]
CMD ["webserver"]

