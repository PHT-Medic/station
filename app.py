import json
import re

from airflow.models import Connection
from airflow.utils.db import provide_session
from flask import Flask, Response, request
from marshmallow import Schema, fields
from marshmallow.validate import Regexp, OneOf, ValidationError
from werkzeug.http import HTTP_STATUS_CODES

_CONN_TYPES = frozenset([
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
])


_SCHEMES = frozenset(['https'])
_PORTS = frozenset([443])

_HEALTHY = 'healthy'
_UNHEALTHY = f'un{_HEALTHY}'


def _is_json(text):
    try:
        json.loads(text)
    except json.decoder.JSONDecodeError:
        raise ValidationError('text is not valid JSON')


_LOWERCASE = Regexp('^[a-z]+$')
_CONN_ID_REGEX = re.compile('^[a-z](?:_?[a-z0-9]+)*$')


# Schema.from_dict unfortunately not available in marshmallow<3.0.0
class ConnectionSchema(Schema):
    conn_id = fields.Str(validate=Regexp(_CONN_ID_REGEX), required=True)
    conn_type = fields.Str(validate=OneOf(_CONN_TYPES), required=True)
    host = fields.Str(validate=_LOWERCASE, required=True)
    schema = fields.Str(OneOf(_SCHEMES), required=True)
    login = fields.Str(validate=_LOWERCASE, required=True)
    password = fields.Str()
    port = fields.Int(validate=OneOf(_PORTS), required=True)
    extra = fields.Str(validate=_is_json)


_CONN_ID = 'conn_id'

# Password omitted on purpose
_CONN_KEYS = frozenset([
    _CONN_ID,
    'conn_type',
    'host',
    'schema',
    'login',
    'port',
    'extra'
])


def _conn_to_dict(conn):
    return {
        key: getattr(conn, key) for key in _CONN_KEYS
    }


_CONNECTIONS = 'connections'
_POST = 'POST'
_PUT = 'PUT'
_GET = 'GET'
_DELETE = 'DELETE'
_APPLICATION_JSON = 'application/json'

_created = Response(status=201)
_no_content = Response(status=204)

app = Flask(__name__)


def _problem_view(status: int, detail: str):
    return Response(
        response=json.dumps({
            'detail': detail,
            'status': status,
            'title': HTTP_STATUS_CODES[status],
            'type': 'about:blank'
        }),
        status=status,
        content_type='application/problem+json')


def _problem_invalid_content_type(content_type):
    return _problem_view(
        status=415,
        detail=f'Content-Type \'{content_type}\' is not supported! Please use \'{_APPLICATION_JSON}\'')


def _get_connection(conn_id, session):
    return session.query(Connection).filter_by(conn_id=conn_id).first()


@app.route(f'/api/{_CONNECTIONS}', methods=[_GET, _POST])
@provide_session
def get_connections(session=None):
    method = request.method
    if method == _GET:
        return {
            _CONNECTIONS: [
                _conn_to_dict(conn) for conn in session.query(Connection).all()
            ]
        }
    elif method == _POST:

        # Check Content Type
        content_type = request.content_type
        if content_type != _APPLICATION_JSON:
            return _problem_invalid_content_type(content_type)

        # Validate request body for schema validity
        conn = ConnectionSchema().load(request.json)
        errors = conn.errors
        if errors:
            return _problem_view(400, detail=str(errors))
        data = conn.data
        conn_id = data[_CONN_ID]
        if _get_connection(conn_id, session):
            return _problem_view(409, detail=f'Conn ID \'{conn_id}\' already exist!')
        conn = Connection(**data)
        session.add(conn)
        # TODO Location Header of new resource not set yet
        return Response(
            status=201,
            response=json.dumps(_conn_to_dict(conn)))


@app.route(f'/api/{_CONNECTIONS}/<conn_id>', methods=[_GET, _DELETE, _PUT])
@provide_session
def get_connection(conn_id, session=None):
    if not _CONN_ID_REGEX.match(conn_id):
        return _problem_view(400, f'Not a valid Conn ID: \'{conn_id}\'')
    connection = _get_connection(conn_id, session)
    if not connection:
        return _problem_view(404, f'Connection: \'{conn_id}\' was not found')

    method = request.method
    if method == _GET:
        return _conn_to_dict(connection)
    elif method == _DELETE:
        session.delete(connection)
        return _no_content
    elif method == _PUT:
        # Check Content Type
        content_type = request.content_type
        if content_type != _APPLICATION_JSON:
            return _problem_invalid_content_type(content_type)

        conn = ConnectionSchema().load(request.json)
        errors = conn.errors
        if errors:
            return _problem_view(400, detail=str(errors))
        if conn.data[_CONN_ID] != conn_id:
            return _problem_view(status=400, detail='Conn ID in request body does not agree with the one in path!')

        for (key, value) in conn.data.items():
            setattr(connection, key, value)
        session.merge(connection)
        return Response(
            status=200,
            response=json.dumps(_conn_to_dict(connection)))


@app.route('/api/health', methods=[_GET])
@provide_session
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
