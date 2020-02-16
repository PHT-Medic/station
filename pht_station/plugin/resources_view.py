import dataclasses

import flask
from flask_admin import BaseView, expose

from pht_trainlib.util import convert_to_serializable
from pht_trainlib.docker_ops import list_volumes
from pht_trainlib.data import DockerVolume

from pht_station.models import Resource
from pht_station.resource_types import DOCKER_VOLUME


from .internal import API, template_path, POST, GET


_template_resources = template_path('resources.html')


@dataclasses.dataclass(frozen=True)
class _DockerVolumeResponse:
    volume: DockerVolume
    resource_key: str


class Resources(BaseView):
    """
    The view for the Station to manage the Resources that it can provide to trains
    """
    ###############################################################
    # Views
    ###############################################################
    @expose('/')
    def resources(self):
        return self.render(_template_resources)

    @expose('/api/volumes')
    def docker_volumes(self):

        # map docker volume names to the respective resource key
        resources = Resource.tabulate(
            key_f=lambda res: res.attributes['name'],
            value_f=lambda res: res.key,
            resource_type_id=DOCKER_VOLUME)

        return {
            'volumes': convert_to_serializable(
                _DockerVolumeResponse(
                    volume=volume,
                    resource_key=resources.get(volume.name)
                ) for volume in list_volumes()
            )
        }

    @expose('/api/resources', methods=(GET, POST))
    def api_resources(self):
        """Returns the resources of the Station"""
        method = flask.request.method.upper()
        if method == GET:
            return {
                'resources': convert_to_serializable(Resource.view_all())
            }
        elif method == POST:
            print(flask.request.get_json(), flush=True)
