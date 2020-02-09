from airflow.plugins_manager import AirflowPlugin

import flask
from flask_admin import BaseView, expose
# from flask_admin.base import MenuLink

# Importing base classes that we need to derive
# from airflow.hooks.base_hook import BaseHook
# from airflow.models import BaseOperator
# from airflow.models.baseoperator import BaseOperatorLink
# from airflow.sensors.base_sensor_operator import BaseSensorOperator
# from airflow.executors.base_executor import BaseExecutor

import requests

from pht_trainlib.util import convert_to_serializable
from pht_station.http_clients import Harbor, create_repo_client

_plugin_name = 'pht_station'
_category = 'PHT Station'

# TODO Move to config
_API_ENDPOINT = 'http://nginx'

# TODO Auth

# Flask Responses
_NO_CONTENT = flask.Response(status=204)


# def get_repositories():
#     response = requests.get(_API_ENDPOINT + '/repository')
#     return response.json()['repositories']
#
#
# def get_tags(repo_id):
#     response = requests.get(_API_ENDPOINT + f'/repository/{repo_id}/tag')
#     return response.json()['tags']

# templates
_template_registry = f'{_plugin_name}/registry.html'
_template_executions = f'{_plugin_name}/executions.html'


class Registry(BaseView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._repo_client = create_repo_client(Harbor(base_url='https://harbor.lukaszimmermann.dev'))

    # @expose('/api/tags', methods=['GET'])
    # def get_tags(self):
    #     return flask.Response(status=209, response=json.dumps({
    #         'foo': 'bar'
    #     }))

    ###############################################################
    # Views
    ###############################################################
    @expose('/')
    def trains(self):
        return self.render(_template_registry,
                           repos=self._repo_client.repositories())

    ###############################################################
    # API
    ###############################################################
    @expose('/api/repository')
    def get_repository(self):
        return {
            'repositories': convert_to_serializable(self._repo_client.repositories())
        }

    @expose('/api/repository/<path:repo_name>/tag')
    def get_tag(self, repo_name):
        return {
            'tags': convert_to_serializable(self._repo_client.tags(repo_name))
        }


class Executions(BaseView):

    # @expose('/api/tags', methods=['GET'])
    # def get_tags(self):
    #     return flask.Response(status=209, response=json.dumps({
    #         'foo': 'bar'
    #     }))

    ###############################################################
    # Views
    ###############################################################
    @expose('/')
    def trains(self):
        return self.render(_template_executions)

    @expose('/api/execute', methods=['POST'])
    def post_execution(self):
        print('foo', flush=True)
        body = flask.request.json()
        print(body, flush=True)
        return _NO_CONTENT

    ###############################################################
    # API
    ###############################################################
    # @expose('/api/repository')
    # def get_repository(self):
    #     return {
    #         'repositories': convert_to_serializable(self._repo_client.repositories())
    #     }
    #
    # @expose('/api/repository/<path:repo_name>/tag')
    # def get_tag(self, repo_name):
    #     return {
    #         'tags': convert_to_serializable(self._repo_client.tags(repo_name))
    #     }


registry_view = Registry(category=_category, name='Registry')
executions_view = Executions(category=_category, name='Executions')

# Creating a flask blueprint to integrate the templates and static folder
bp = flask.Blueprint(
    _plugin_name, __name__,
    template_folder='templates',  # registers airflow/plugins/templates as a Jinja template folder
    static_folder='static',
    static_url_path=f'/static/{_plugin_name}')

# ml = MenuLink(
#     category='Test Plugin',
#     name='Test Menu Link',
#     url='https://airflow.apache.org/')


# Creating a flask appbuilder BaseView
# class TestAppBuilderBaseView(BaseView):
#     @expose("/")
#     def test(self):
#         return self.render("test_plugin/test.html", content="Hello galaxy!")


# v_appbuilder_view = TestAppBuilderBaseView()
# v_appbuilder_package = {"name": "Test View",
#                         "category": "Test Plugin",
#                         "view": v_appbuilder_view}

# Creating a flask appbuilder Menu Item
# appbuilder_mitem = {"name": "Google",
#                     "category": "Search",
#                     "category_icon": "fa-th",
#                     "href": "https://www.google.com"}


class AirflowTestPlugin(AirflowPlugin):
    name = 'pht_station'
    admin_views = [registry_view, executions_view]
    flask_blueprints = [bp]
    menu_links = []
    appbuilder_views = []
    appbuilder_menu_items = []
