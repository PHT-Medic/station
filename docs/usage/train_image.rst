Train Images
============
Train Images are Docker Images which are defined hierarchically defined:


A regular container image becomes a train image via the presence of at least one so-called `endpoint`.
An endpoint is a directory with the following path::

    /opt/pht_train/endpoints/<endpoint_name>

Endpoints can be filled with several `train commands`. A train command [is a path with the following
structure::

    /opt/pht_train/endpoints/<endpoint_name>/commands/<command_name>

For a command to become executable by the station, an executable file, the `entrypoint` needs to be added with the following structure::

    /opt/pht_train/endpoints/<endpoint_name>/commands/<command_name>/entrypoint<file_extension>

Note that only the basename of the file is relevant to signify it as entrypoint.

Commands
--------

For a given endpoint ``endpoint_name``, a command ``command_name`` is a directory ``DIR=/opt/pht_train/endpoints/endpoint_name/commands/command_name``.
Commands are those entities in the container image that are translated to entrypoints for a respective started container.
If ``DIR`` does not contain any directories, there is no command for that endpoint a container for this endpoint cannot be
created. 

There is one special name for a command, which is ``run``. This is the source for the created container if the command is not
explicitly specified otherwise.

Command Files
~~~~~~~~~~~~~

The following table gives a list of files that are currently recognized for a command:

+--------------------------------+-------------------------------------------------------------------------------+-------------------+
| Filename                       | Description                                                                   | Required (yes/no) |
+================================+===============================================================================+===================+
| ``README.md``                  | Markdown Content for describing the command                                   |       no          |
+--------------------------------+-------------------------------------------------------------------------------+-------------------+
| ``RESOURCES.tsv``              | The resource descriptor. See below for details.                               |       no          |
+--------------------------------+-------------------------------------------------------------------------------+-------------------+
| ``entrypoint.<fileextension>`` | The entrypoint file for the container. Multiple such files are a fatal error. |       yes         |
+--------------------------------+-------------------------------------------------------------------------------+-------------------+

The Resource Descriptor
-----------------------

Each command can describe which resources it requires from the Station.
For a given entrypoint ``entrypoint_name`` and command ``command_name``, the file::

    /opt/pht_train/endpoints/<endpoints_name>/commands/<command_name>/RESOURCES.tsv

describes the resources that the command requires from the station to be executed.

Each line in this file represents a resource that the commands declares to the Station. A line has
the following schema::

<key>

The individual fields are separated by the TAB character and have the following semantics:

+---------+-------------------------------------------------------------------+
| <key>   |  What resource the train wants                                    |
+---------+-------------------------------------------------------------------+
