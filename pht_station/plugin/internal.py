import flask

API = 'api'
PLUGIN_NAME = 'pht_station'
POST = 'POST'
GET = 'GET'

# Flask Responses
NO_CONTENT = flask.Response(status=204)


def template_path(filename: str) -> str:
    return f'{PLUGIN_NAME}/{filename}'
