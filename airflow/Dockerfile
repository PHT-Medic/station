FROM bitnami/python:3.10.11-debian-11-r13

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
# install train container library
RUN pip install --force-reinstall --no-cache-dir -v "pht-train-container-library==2.0.5"

RUN mkdir /opt/train_data

COPY airflow.cfg /root/airflow/airflow.cfg
COPY ./dags /root/airflow/dags

COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

# uninstall curl/libcurl3-gnutls from the image
RUN apt-get remove -y libcurl3-gnutls && \
    apt-get remove -y libcurl4 && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists

ENTRYPOINT ["/root/entrypoint.sh"]
CMD ["webserver"]

