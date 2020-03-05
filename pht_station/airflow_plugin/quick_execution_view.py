import flask
from flask_admin import BaseView, expose
from flask_wtf import FlaskForm
from wtforms import RadioField
import pht_trainlib.util as util
import pht_station.airflow as airflow
from pht_station.http_clients import Harbor, create_repo_client
from .internal import template_path, GET, POST


_template_quick_execution = template_path('quick_execution')


class QuickExecutionForm(FlaskForm):
    image = RadioField('image')


class QuickExecution(BaseView):
    """
    View used to list all the tran
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._container_registry_host = util.without_suffix(
            airflow.get_container_registry_host(),
            suffix='/')
        self._repo_client = create_repo_client(
            Harbor(base_url=f'https://{self._container_registry_host}')
        )

    ###############################################################
    # Views
    ###############################################################
    @expose('/', methods=(GET, POST))
    def index(self):
        method = flask.request.method
        if method == GET:
            return self.render(_template_quick_execution,
                               form=QuickExecutionForm(),
                               repotags=({
                                   'repo': repo_tag[0],
                                   'tag': repo_tag[1]
                               } for repo_tag in self._repo_client.repo_tags()))
        elif method == POST:
            dag_id = airflow.DAG_QUICK
            image = flask.request.form.get('image')
            # TODO What to do with run?
            execution_date = airflow.trigger(dag_id=dag_id, conf={
                'image': f'{self._container_registry_host}/{image}'
            }).execution_date
            return flask.redirect(
                flask.url_for(
                    'airflow.graph', dag_id=dag_id, execution_date=execution_date))
