Tutorial
=============================

Setting the Station ID
----------------------
If you run stationctl, you will notice that only the subcommand `config` is available.
This is due to the fact that each Station needs to be assigned a unique Station ID 


Attaching to the Registry
-------------------------

The Station needs to be informed on all remote registries that contain trains
which the Station wants to execute. For this, the registry needs to be added to the Station's Database.

With the command line tool `stationctl`, a registry can be added with the following call::

    stationctl registry create --host <registry_host> --login <username> --password <password>

where `<registry_host>`, `<username>`, and `<password>` have to be set to their respective values.
Make sure that the command runs successfully.

To verify that the registry has been added, you can run::

    stationctl registry ls

A registry can be deleted via::

    stationctl registry delete <registry_id>

A registry needs to be attached, such that train images can be pulled and pushed backed after the analysis is complete.



Behind the scenes in Airflow:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each registry is identified with an Airflow `Connection` of type http.
The `conn_id` attribute is set to 
    
    pht-station-registry-<registry_id>

so there is a direct mapping between registry ids (as reported by `registry ls`) and conn_ids.
Hence, you can also manage registries via the Airflow Webinterface, when you look for such conn_ids.
