import flask
from flask_admin import BaseView, expose
import pht_trainlib.util as util
import pht_station.airflow as airflow
from pht_station.http_clients import Harbor, create_repo_client

from .internal import template_path, GET, POST


_template_registry = template_path('registry')


class Registry(BaseView):
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
            return self.render(_template_registry,
                               repotags=({
                                   'repo': repo_tag[0],
                                   'tag': repo_tag[1]
                               } for repo_tag in self._repo_client.repo_tags()))

    # ###############################################################
    # # API
    # ###############################################################
    # @expose(f'/{API}/repository')
    # def get_repository(self):
    #     return {
    #         'repositories': convert_to_serializable(self._repo_client.repositories())
    #     }
    #
    # @expose(f'/{API}/repository/<path:repo_name>/tag')
    # def get_tag(self, repo_name):
    #     return {
    #         'tags': convert_to_serializable(self._repo_client.tags(repo_name))
    #     }

    # # TODO Docment request body here
    # @expose(f'/{API}/train', methods=(POST, ))
    # def train(self):
    #     """
    #     Creates a train from a specified repository and tag
    #     """
    #     body = flask.request.get_json()
    #     validate_request_body_for_train(body)
    #     repo = body['repo']
    #     tag = body['tag']
    #     digest = body['digest']
    #
    #     tracker = Tracker.upsert(repository=repo, tag=tag)
    #     manifest_id = _load_manifest(repo=repo, tag=tag, repo_client=self._repo_client)
    #     tracker_identity_id, inserted = TrackerIdentity.upsert(
    #         tracker_id=tracker.id,
    #         docker_image_manifest_id=manifest_id,
    #         digest_tag_harbor=digest)
    #     if inserted:
    #         # a new dag needs to be triggered for newly inserted identities
    #         run = airflow.trigger(dag_id=airflow.DAG_INSPECT, conf={
    #             'tracker_identity': _view(int(tracker_identity_id))
    #         })
    #         # TODO Link run info with tracker_identity?
    #
    #     return NO_CONTENT

#
# def validate_request_body_for_train(body):
#     # TODO
#     pass
#
#
# def _load_manifest(repo: str, tag: str, repo_client) -> int:
#     """Loads the manifest of this repo/tag and returns the primary key"""
#     manifest, _ = repo_client.image_metadata(repo_name=repo, tag=tag)
#     manifest_skel = _create_skeleton(manifest=manifest)
#
#     manifest_id = DockerImageManifest.insert(manifest_skel)
#     return manifest_id
#
#
# def _create_skeleton(manifest: ImageManifest) -> ImageManifestSkeleton:
#     """
#     Inserts all hash values of the file system layers into the database for this image.
#     Raises Value error if there is a hash value which is not sha256
#     """
#     manifest_config = manifest.config
#     manifest_layers = manifest.layers
#
#     # 0. Media Types
#     manifest_media_types = list(MediaType.get_primary_keys(
#         itertools.chain(
#             (manifest.mediaType, manifest_config.mediaType),
#             (layer.mediaType for layer in manifest_layers))))
#
#     # 1. Hash Values, Manifest are marked True, configs are marked False
#     manifest_hash_values = list(HashValueSHA256.upsert_all(
#         itertools.chain([manifest_config.digest], (layer.digest for layer in manifest_layers))))
#
#     manifest_skel = ImageManifestSkeleton(
#         schemaVersion=manifest.schemaVersion,
#         mediaType=manifest_media_types[0],
#         config_media_type=manifest_media_types[1],
#         config_size=manifest_config.size,
#         config_digest=manifest_hash_values[0],
#         layer_media_types=manifest_media_types[2:],
#         layer_sizes=[layer.size for layer in manifest_layers],
#         layer_digests=manifest_hash_values[1:])
#
#     return manifest_skel
#
#
# def _view(tracker_identity_id: int):
#     return convert_to_serializable(TrackerIdentity.view(tracker_identity_id))
