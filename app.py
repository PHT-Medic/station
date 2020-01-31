#!/usr/bin/env python
import base64
import json
import pickle
import re
import typing

import airflow
import airflow.utils.db
import flask
import marshmallow
import marshmallow.validate
import werkzeug

from pht_trainlib.util import require_valid_hostname

# String constants
_DAG = 'dag'
_DAGS = f'{_DAG}s'
_DAG_RUNS = f'{_DAG}_runs'
_CONN_ID = 'conn_id'
_DAG_ID = f'{_DAG}_id'
_ROOT_DAG_ID = f'root_{_DAG_ID}'
_CONNECTIONS = 'connections'
_POST = 'POST'
_PUT = 'PUT'
_GET = 'GET'
_DELETE = 'DELETE'
_APPLICATION_JSON = 'application/json'
_HEALTHY = 'healthy'
_UNHEALTHY = f'un{_HEALTHY}'


# Flask Responses
_NO_CONTENT = flask.Response(status=204)

# Other constant values
_JSON_SEPS = (',', ':')


# conn_types supported by Apache Airflow, used for validation
_CONN_TYPES = (
    'docker',
    'fs',
    'ftp',
    'google_cloud_platform',
    'hdfs',
    'http',
    'pig_cli',
    'hive_cli',
    'hive_metastore',
    'hiveserver2',
    'jdbc',
    'jenkins',
    'mysql',
    'postgres',
    'oracle',
    'vertica',
    'presto',
    's3',
    'samba',
    'sqlite',
    'ssh',
    'cloudant',
    'mssql',
    'mesos_framework-id',
    'jira',
    'redis',
    'wasb',
    'databricks',
    'aws',
    'emr',
    'snowflake',
    'segment',
    'azure_data_lake',
    'azure_container_instances',
    'azure_cosmos',
    'cassandra',
    'qubole',
    'mongo',
    'gcpcloudsql',
    'grpc'
)


_SCHEMES = frozenset(['https'])
_PORTS = frozenset([443])


_ENCODING = 'utf-8'


def _is_json(text):
    try:
        json.loads(text)
    except json.decoder.JSONDecodeError:
        raise marshmallow.validate.ValidationError('text is not valid JSON')


_LOWERCASE = marshmallow.validate.Regexp('^[a-z]+$')
_CONN_ID_REGEX = re.compile('^[a-z](?:_?[a-z0-9]+)*$')


def _validate_hostname(text):
    try:
        require_valid_hostname(text)
    except ValueError:
        raise marshmallow.validate.ValidationError(f'Not a valid hostname: \'{text}\'')


# # Schema.from_dict unfortunately not available in marshmallow<3.0.0
class ConnectionSchema(marshmallow.Schema):
    conn_id = marshmallow.fields.Str(validate=marshmallow.validate.Regexp(_CONN_ID_REGEX), required=True)
    conn_type = marshmallow.fields.Str(validate=marshmallow.validate.OneOf(_CONN_TYPES), required=True)
    host = marshmallow.fields.Str(validate=_validate_hostname, required=True)
    schema = marshmallow.fields.Str(marshmallow.validate.OneOf(_SCHEMES), required=False)
    login = marshmallow.fields.Str(validate=_LOWERCASE, required=False)
    password = marshmallow.fields.Str(required=False)
    port = marshmallow.fields.Int(validate=marshmallow.validate.OneOf(_PORTS), required=False)
    extra = marshmallow.fields.Str(validate=_is_json, required=False)


def _encode_obj(obj) -> str:
    return base64.standard_b64encode(pickle.dumps(obj)).decode(_ENCODING)


class Mapper:
    """
    Maps an object to a dictionary with keys specified by items
    """
    def __init__(self, items):
        self._items = tuple(items)

    def __call__(self, *args, **kwargs):
        arg = args[0]
        if isinstance(arg, typing.Iterable):
            result = self._map_all(arg)
        else:
            result = self._map(arg)
        return result

    @staticmethod
    def _identity(x):
        return x

    def _map(self, obj):
        result = {}
        for attr in self._items:
            if isinstance(attr, typing.Sequence) and len(attr) == 2 and not isinstance(attr, str):
                key = attr[0]
                f = attr[1]
            else:
                key = attr
                f = self._identity
            result[key] = f(getattr(obj, key))
        return result

    def _map_all(self, objs):
        yield from (self._map(obj) for obj in objs)


_map_conn = Mapper([
    _CONN_ID,
    'conn_type',
    'host',
    'schema',
    'login',
    'port',
    'extra'
])

_map_dag = Mapper([
    _DAG_ID,
    _ROOT_DAG_ID,
    'is_paused',
    'is_subdag',
    'is_active',
    'scheduler_lock',
    'pickle_id',
    'fileloc',
    'owners',
    'description',
    'default_view'
])

_map_dag_run = Mapper([
    'id',
    _DAG_ID,
    'execution_date',
    'start_date',
    'end_date',
    'state',
    'run_id',
    'external_trigger',
    ('conf', _encode_obj)
])


app = flask.Flask(__name__)


def _problem_view(status: int, detail: str):
    return flask.Response(
        response=json.dumps({
            'detail': detail,
            'status': status,
            'title': werkzeug.http.HTTP_STATUS_CODES[status],
            'type': 'about:blank'
        }),
        status=status,
        content_type='application/problem+json')


def _problem_invalid_content_type(content_type):
    return _problem_view(
        status=415,
        detail=f'Content-Type \'{content_type}\' is not supported! Please use \'{_APPLICATION_JSON}\'')


def _get_connection(conn_id, session):
    return session.query(airflow.models.Connection).filter_by(conn_id=conn_id).first()


def _get_all_connections(session):
    return session.query(airflow.models.Connection).all()


@app.route(f'/api/{_CONNECTIONS}', methods=[_GET, _POST, _DELETE])
@airflow.utils.db.provide_session
def connections(session=None):
    method = flask.request.method
    if method == _GET:
        return {
            _CONNECTIONS: list(_map_conn(_get_all_connections(session)))
        }

    elif method == _DELETE:
        for conn in _get_all_connections(session):
            session.delete(conn)
        return _NO_CONTENT

    elif method == _POST:
        # Check Content Type
        content_type = flask.request.content_type
        if content_type != _APPLICATION_JSON:
            return _problem_invalid_content_type(content_type)

        # Validate request body for schema validity
        conn = ConnectionSchema().load(flask.request.json)

        # TODO Validation disabled
        # errors = conn.errors
        # if errors:
        #     return _problem_view(400, detail=str(errors))
        data = conn.data
        conn_id = data[_CONN_ID]
        if _get_connection(conn_id, session):
            return _problem_view(409, detail=f'Conn ID \'{conn_id}\' already exist!')
        conn = airflow.models.Connection(**data)
        session.add(conn)
        # TODO Location Header of new resource not set yet
        return flask.Response(
            status=201,
            response=json.dumps(_map_conn(conn)))


@app.route(f'/api/{_CONNECTIONS}/<conn_id>', methods=[_GET, _DELETE, _PUT])
@airflow.utils.db.provide_session
def get_connection(conn_id, session=None):
    if not _CONN_ID_REGEX.match(conn_id):
        return _problem_view(400, f'Not a valid Conn ID: \'{conn_id}\'')
    connection = _get_connection(conn_id, session)
    if not connection:
        return _problem_view(404, f'Connection: \'{conn_id}\' was not found')

    method = flask.request.method
    if method == _GET:
        return _map_conn(connection)
    elif method == _DELETE:
        session.delete(connection)
        return _NO_CONTENT
    elif method == _PUT:
        # Check Content Type
        content_type = flask.request.content_type
        if content_type != _APPLICATION_JSON:
            return _problem_invalid_content_type(content_type)

        conn = ConnectionSchema().load(flask.request.json)

        # TODO Validation disabled
        # errors = conn.errors
        # if errors:
        #     return _problem_view(400, detail=str(errors))
        if conn.data[_CONN_ID] != conn_id:
            return _problem_view(status=400, detail='Conn ID in request body does not agree with the one in path!')

        for (key, value) in conn.data.items():
            setattr(connection, key, value)
        session.merge(connection)
        return flask.Response(
            status=200,
            response=json.dumps(_map_conn(connection)))


@app.route(f'/api/{_DAGS}', methods=[_GET])
@airflow.utils.db.provide_session
def get_dags(session=None):
    dags = session.query(airflow.models.DagModel).all()
    return {
        _DAGS: list(_map_dag(dags))
    }


@app.route(f'/api/{_DAGS}/<dag_id>/{_DAG_RUNS}', methods=[_GET])
@airflow.utils.db.provide_session
def get_dag_runs(dag_id, session=None):
    dag_runs = session.query(airflow.models.DagRun).filter_by(dag_id=dag_id).all()
    return {
        _DAG_RUNS: list(_map_dag_run(dag_runs))
    }


@app.route(f'/api/{_DAG_RUNS}', methods=[_GET])
@airflow.utils.db.provide_session
def get_all_dag_runs(session=None):
    dag_runs = session.query(airflow.models.DagRun).all()
    return {
        _DAG_RUNS: list(_map_dag_run(dag_runs))
    }


@app.route('/api/health', methods=[_GET])
@airflow.utils.db.provide_session
def get_health(session=None):
    try:
        session.execute('SELECT 1')
        status = _HEALTHY
    except:
        status = _UNHEALTHY
    return {
        'health': {
            'status': status
        }
    }


if __name__ == '__main__':
    app.run('0.0.0.0', port=4000)
