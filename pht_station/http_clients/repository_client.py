# """
# Contains the specification of a Repository Client
#
# A Repository Client is a thing that can be asked for repositories
# """
# import abc
# import concurrent.futures
# import dataclasses
# import types
# import typing
#
# # import pht_trainlib.data as data
# from .harbor import Harbor
#
#
# @dataclasses.dataclass(frozen=True)
# class Repository:
#     id: int
#     name: str
#     description: str
#
#
# @dataclasses.dataclass(frozen=True)
# class Tag:
#     name: str
#     digest: str
#     size: int
#     architecture: str
#     os: str
#     os_version: typing.Optional[str]
#     author: str
#     created: str
#
#
# class RepositoryClient(abc.ABC):
#
#     @abc.abstractmethod
#     def repositories(self) -> typing.Iterable[Repository]:
#         """Returns a list of all repositories that a client has access to"""
#
#     @abc.abstractmethod
#     def tags(self, repo_name: str) -> typing.Iterable[Tag]:
#         """Return list of all tags associated with this repository"""
#
#     @abc.abstractmethod
#     def image_metadata(self, repo_name: str, tag: str) -> typing.Tuple[data.ImageManifest, typing.Any]:
#         """Returns the metadata of a remote image."""
#
#     def repo_tags(self) -> typing.Iterable[typing.Tuple[Repository, Tag]]:
#         yield from (
#             (repo, tag) for repo in self.repositories() for tag in self.tags(repo.name)
#         )
#
#
# def _get(obj, attr):
#     if isinstance(obj, typing.Mapping):
#         return obj[attr]
#     return getattr(obj, attr)
#
#
# def create_repo_client(client) -> RepositoryClient:
#     if isinstance(client, Harbor):
#         return _HarborRepoClient(client)
#     raise TypeError('Client is not something that you can turn into a RepositoryClient')
#
#
# class _HarborRepoClient(RepositoryClient):
#     def __init__(self, client: Harbor):
#         self._client = client
#         # Maps repo_ids to their respective names
#         self._repo_names = {}
#
#     def repositories(self) -> typing.Iterable[Repository]:
#         # NB: Harbor only supports listing repositories by project_jd. Hence we need to fetch all the projects first
#         project_ids = (proj.project_id for proj in self._client.get_projects())
#         result = []
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             for repos in executor.map(self._client.get_repositories, project_ids):
#                 result.extend(
#                     Repository(name=repo.name, description=repo.description, id=repo.id) for repo in repos
#                 )
#         return result
#
#     def tags(self, repo_name: str) -> typing.Iterable[Tag]:
#         yield from (
#             Tag(
#                 name=_get(tag, 'name'),
#                 digest=_get(tag, 'digest'),
#                 size=_get(tag, 'size'),
#                 architecture=_get(tag, 'architecture'),
#                 os=_get(tag, 'os'),
#                 os_version=_get(tag, 'os_version'),
#                 author=_get(tag, 'author'),
#                 created=_get(tag, 'created')
#             ) for tag in self._client.get_tags(repo_name)
#         )
#
#     def image_metadata(self, repo_name: str, tag: str) -> typing.Tuple[data.ImageManifest, typing.Any]:
#         """Returns Metadata for the selected image.
#
#         The first component is the image Manifest.
#         The second component is populated implementation-specifically
#         """
#         response = self._client.get_manifest(repo_name=repo_name, tag=tag)
#         return response.manifest, types.MappingProxyType({'config': response.config})
