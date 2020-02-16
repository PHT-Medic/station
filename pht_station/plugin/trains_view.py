import flask
from flask_admin import BaseView, expose

from pht_trainlib.util import convert_to_serializable
from pht_station.models import TrackerIdentity, Processing
import pht_station.airflow as airflow

from .internal import API, template_path, POST, NO_CONTENT


_template_trains = template_path('trains.html')


class Trains(BaseView):

    ###############################################################
    # Views
    ###############################################################
    @expose('/')
    def trains(self):
        # The UI will refer to the TrackerIdentities as Trains
        return self.render(_template_trains, trains=TrackerIdentity.view_all())

    ###############################################################
    # API
    ###############################################################
    @expose(f'/{API}/trackeridentity')
    def trackeridentity_index(self, tracker_identity_id):
        pass

    @expose(f'/{API}/trackeridentity/<tracker_identity_id>')
    def trackeridentity(self, tracker_identity_id):
        return convert_to_serializable(
            TrackerIdentity.get_identity_data(tracker_identity_id)
        )

    @expose(f'/{API}/process', methods=(POST, ))
    def process(self):
        """Starts a new processing for the specified tracker_identity_id"""
        body = flask.request.get_json()
        _validate_body_for_process(body)
        tracker_identity_id = body['trackerIdentityId']

        # TODO Share session
        tracker = TrackerIdentity.view(tracker_identity_id).tracker
        proc_id = Processing.create(tracker_identity_id=tracker_identity_id)
        airflow.trigger(dag_id=airflow.DAG_PROCESS, conf={
            'processing_id': proc_id,
            'repository': tracker.repository,
            'tag': tracker.tag,
            'tracker_identity_id': tracker_identity_id
        })
        return NO_CONTENT


def _validate_body_for_process(body):
    # TODO
    pass
