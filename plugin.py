import flask
from airflow.plugins_manager import AirflowPlugin
from pht_station.airflow_plugin import \
    QuickExecution,\
    Registry, \
    RunningTrains, \
    PLUGIN_NAME


_category = 'PHT Station'


class PHTStationPlugin(AirflowPlugin):
    name = PLUGIN_NAME
    admin_views = [
        Registry(category=_category, name='Registry'),
        RunningTrains(category=_category, name='Running Train'),
        # Resources(category=_category, name='Resources'),
        # Trains(category=_category, name='Trains'),
        # Processings(category=_category, name='Processings'),
        QuickExecution(category=_category, name='Quick Execution')
    ]
    flask_blueprints = [
        flask.Blueprint(
            PLUGIN_NAME + '_templates', __name__,
            template_folder='templates'),
        flask.Blueprint(
            PLUGIN_NAME + '_images', __name__,
            static_folder='static',
            static_url_path='/images')
    ]
    menu_links = []
    appbuilder_views = []
    appbuilder_menu_items = []
