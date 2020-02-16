Installation Guide
==================

The Station requires Apache Airflow for scheduling and executing train images.
In addition, the Station-specific components are deployed via one ``docker-compose.yml`` file.


Setting up Apache Airflow
-------------------------

Follow the instructions in the ``README.md`` file here::

    git@gitlab.com:PersonalHealthTrain/implementations/germanmii/difuture/station/airflow-rest-api.git


Setting up the Station Components
---------------------------------

Follow the instructions in the ``README.md`` file here::

    git@gitlab.com:PersonalHealthTrain/implementations/germanmii/difuture/station/station.git




.. There are two PostgreSQL databases, which are relevant for the Station:

.. - The database for Apache Airflow (named **airflow** henceforth).. _Airflow: https://airflow.apache.org/docs/stable/installation.html

.. - The database for the Station (named **station** henceforth)

.. The database was tested with PostgreSQL 12.1 and currently needs to be set up manually.

.. .. NOTE::
..    Here we assume that the **airflow** and **station** database are part of the same
..    PostgreSQL DBMS. You can of course change that to whichever configuration is
..    suitable for you.

.. 0. Pick a machine that hosts the DBMS.

.. 1. Install Postgres 12.1. You can do this whichever way suits best for you, we recommend the official Postgres Docker image,
..    which is available on Docker Hub (and please make yourself familiar with the mechanism of Docker volumes if you do so).

.. 2. Create the `airflow` user with the following query::

..     CREATE USER airflow NOSUPERUSER NOCREATEDB PASSWORD 'airflow-password';

.. 3. Create the **airflow** database with the following query::

..     CREATE DATABASE "airflow"
..         WITH OWNER "airflow"
..         LC_COLLATE = 'en_US.UTF-8'
..         LC_CTYPE = 'en_US.UTF-8';

.. 4. Grant permissions::
   
..     GRANT ALL ON DATABASE airflow to airflow;
   

.. 5. Create the `station` user with the following query::
    
..     CREATE USER station NOSUPERUSER NOCREATEDB PASSWORD 'station-password';
    

.. 6. Create the **station** database with the following query::
   
..     CREATE DATABASE "station"
..         WITH OWNER "station"
..         ENCODING 'UTF8'
..         LC_COLLATE = 'en_US.UTF-8'
..         LC_CTYPE = 'en_US.UTF-8';


.. 7. Grant permissions::

..     GRANT ALL ON DATABASE station to station;

.. This will create the databases for the applications, the tables will be created later.
