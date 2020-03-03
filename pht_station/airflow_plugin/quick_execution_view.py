import flask
from flask_admin import BaseView, expose
from flask_wtf import FlaskForm
from wtforms import RadioField

from pht_station.http_clients import Harbor, create_repo_client
from .internal import template_path, GET, POST, NO_CONTENT


_template_quick_execution = template_path('quick_execution')


class QuickExecutionForm(FlaskForm):
    image = RadioField('image')


class QuickExecution(BaseView):
    """
    View used to list all the tran
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._repo_client = create_repo_client(Harbor(base_url='https://harbor.lukaszimmermann.dev'))

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
            image = flask.request.form.get('image')
            print(image, flush=True)
            return NO_CONTENT
