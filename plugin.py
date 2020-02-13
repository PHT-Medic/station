import dataclasses
from itertools import chain, tee

from airflow.plugins_manager import AirflowPlugin
import flask
from flask_admin import BaseView, expose

from pht_trainlib.util import convert_to_serializable
from pht_trainlib.docker_ops import list_volumes
from pht_trainlib.data import DockerVolume, ImageManifest

from pht_station.http_clients import Harbor, create_repo_client
from pht_station.resource_types import DOCKER_VOLUME
from pht_station.models import \
    Resource, TrackerIdentity, Tracker, ImageManifestSkeleton, DockerImageManifest, MediaType, HashValueSHA256


_plugin_name = 'pht_station'
_category = 'PHT Station'

# TODO Move to config
_API_ENDPOINT = 'http://nginx'

# TODO Auth

# Flask Responses
_NO_CONTENT = flask.Response(status=204)

# HTTP Methods
GET = 'GET'
POST = 'POST'


# templates
_template_registry = f'{_plugin_name}/registry.html'
_template_executions = f'{_plugin_name}/executions.html'
_template_resources = f'{_plugin_name}/resources.html'


# Prefix for routes that are APIs (the ones with JSON)
_API = 'api'


def validate_request_body_for_train(body):
    # TODO
    pass


@dataclasses.dataclass(frozen=True)
class DockerVolumeResponse:
    volume: DockerVolume
    resource_key: str


class Registry(BaseView):
    """
    View used to list all the tran
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._repo_client = create_repo_client(Harbor(base_url='https://harbor.lukaszimmermann.dev'))

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
    @expose(f'/{_API}/repository')
    def get_repository(self):
        return {
            'repositories': convert_to_serializable(self._repo_client.repositories())
        }

    @expose(f'/{_API}/repository/<path:repo_name>/tag')
    def get_tag(self, repo_name):
        return {
            'tags': convert_to_serializable(self._repo_client.tags(repo_name))
        }

    # TODO Docment request body here
    @expose(f'/{_API}/train', methods=(POST, ))
    def train(self):
        """
        Creates a train from a specified repository and tag
        """
        body = flask.request.get_json()
        repo = body['repo']
        tag = body['tag']
        digest = body['digest']

        validate_request_body_for_train(body)

        tracker_id = Tracker.upsert(repository=repo, tag=tag).tracker_id
        manifest_id = _load_manifest(repo=repo, tag=tag, repo_client=self._repo_client)
        TrackerIdentity.upsert(
            tracker_id=tracker_id,
            docker_image_manifest_id=manifest_id,
            digest_tag_harbor=digest)

        return _NO_CONTENT


class Executions(BaseView):

    ###############################################################
    # Views
    ###############################################################
    @expose('/')
    def trains(self):
        return self.render(_template_executions)


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
                DockerVolumeResponse(
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


registry_view = Registry(category=_category, name='Registry')
executions_view = Executions(category=_category, name='Executions')
resources_view = Resources(category=_category, name='Resources')

# Creating a flask blueprint to integrate the templates and static folder
bp = flask.Blueprint(
    _plugin_name, __name__,
    template_folder='templates',  # registers airflow/plugins/templates as a Jinja template folder
    static_folder='static',       # registers airflow/plugins/static
    static_url_path='/images')

# ml = MenuLink(
#     category='Test Plugin',
#     name='Test Menu Link',
#     url='https://airflow.apache.org/')


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
    admin_views = [registry_view, executions_view, resources_view]
    flask_blueprints = [bp]
    menu_links = []
    appbuilder_views = []
    appbuilder_menu_items = []


def _load_manifest(repo: str, tag: str, repo_client) -> int:
    """Loads the manifest of this repo/tag and returns the primary key"""
    manifest, _ = repo_client.image_metadata(repo_name=repo, tag=tag)
    manifest_skel = _create_skeleton(manifest=manifest)

    manifest_id = DockerImageManifest.insert(manifest_skel)
    return manifest_id


def _create_skeleton(manifest: ImageManifest) -> ImageManifestSkeleton:
    """
    Inserts all hash values of the file system layers into the database for this image.
    Raises Value error if there is a hash value which is not sha256
    """
    manifest_config = manifest.config
    manifest_layers = manifest.layers

    # 0. Media Types
    manifest_media_types = list(MediaType.get_primary_keys(
        chain(
            (manifest.mediaType, manifest_config.mediaType),
            (layer.mediaType for layer in manifest_layers))))

    # 1. Hash Values, Manifest are marked True, configs are marked False
    manifest_hash_values = list(HashValueSHA256.upsert_all(
        chain([manifest_config.digest], (layer.digest for layer in manifest_layers))))

    manifest_skel = ImageManifestSkeleton(
        schemaVersion=manifest.schemaVersion,
        mediaType=manifest_media_types[0],
        config_media_type=manifest_media_types[1],
        config_size=manifest_config.size,
        config_digest=manifest_hash_values[0],
        layer_media_types=manifest_media_types[2:],
        layer_sizes=[layer.size for layer in manifest_layers],
        layer_digests=manifest_hash_values[1:])

    return manifest_skel
