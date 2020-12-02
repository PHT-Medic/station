# """
# Marshmallow Schemata for Harbor Client
# """
# import dataclasses
# import enum
# import typing
#
# import marshmallow_dataclass
# import uplink
#
# import pht_trainlib.data as data
# import pht_station.http_clients.handler as handler
#
#
# # TODO Order
# class Severity(enum.Enum):
#     HIGH = 'high'
#     MEDIUM = 'medium'
#     low = 'low'
#     NEGLIGIBLE = 'negligible'
#
#
# class Architecture(enum.Enum):
#     amd64 = 'amd64'
#
#
# class OS(enum.Enum):
#     linux = 'linux'
#
#
# class HarborImageScanStatus(enum.Enum):
#     finished = 'finished'
#
#
# class HarborComponentHealthStatus(enum.Enum):
#     healthy = 'healthy'
#     unhealthy = 'unhealthy'
#
#
# ##
# # Schemas
# ##
#
# @dataclasses.dataclass(frozen=True)
# class HarborProjectMetadata:
#     auto_scan: typing.Optional[bool]
#     enable_content_trust: typing.Optional[bool]
#     prevent_vul: typing.Optional[bool]
#     public: bool
#     reuse_sys_cve_whitelist: typing.Optional[bool]
#     severity: typing.Optional[Severity]
#
#
# HarborProjectMetadataSchema = marshmallow_dataclass.class_schema(HarborProjectMetadata)
#
#
# @dataclasses.dataclass(frozen=True)
# class CveWhitelist:
#     id: int
#     project_id: int
#     items: typing.Optional[typing.List[str]]
#     creation_time: str
#     update_time: str
#
#
# CveWhitelistSchema = marshmallow_dataclass.class_schema(CveWhitelist)
#
#
# @dataclasses.dataclass(frozen=True)
# class HarborProject:
#     project_id: int
#     owner_id: int
#     name: str
#     creation_time: str
#     update_time: str
#     deleted: bool
#     owner_name: str
#     togglable: typing.Optional[bool]
#     current_user_role_id: typing.Optional[int]
#     current_user_role_ids: typing.Optional[int]
#     repo_count: int
#     chart_count: int
#     metadata: HarborProjectMetadata
#     cve_whitelist: CveWhitelist
#
#
# HarborProjectSchema = marshmallow_dataclass.class_schema(HarborProject)
#
#
# @dataclasses.dataclass(frozen=True)
# class HarborRepository:
#     id: int
#     name: str
#     project_id: int
#     description: str
#     pull_count: int
#     star_count: int
#     tags_count: int
#     labels: typing.List[str]
#     creation_time: str
#     update_time: str
#
#
# HarborRepositorySchema = marshmallow_dataclass.class_schema(HarborRepository)
#
#
# @dataclasses.dataclass(frozen=True)
# class ManifestConfig:
#     mediaType: str
#     size: int
#     digest: str
#
#
# ManifestConfigSchema = marshmallow_dataclass.class_schema(ManifestConfig)
#
#
# @dataclasses.dataclass(frozen=True)
# class ManifestLayer:
#     mediaType: str
#     size: int
#     digest: str
#
#
# ManifestLayerSchema = marshmallow_dataclass.class_schema(ManifestLayer)
#
#
# @dataclasses.dataclass(frozen=True)
# class ManifestResponse:
#     manifest: data.ImageManifest
#     config: str
#
#
# ManifestResponseSchema = marshmallow_dataclass.class_schema(ManifestResponse)
#
#
# @dataclasses.dataclass(frozen=True)
# class HarborImageConfig:
#     labels: typing.Optional[typing.List[str]]
#
#
# HarborImageConfigSchema = marshmallow_dataclass.class_schema(HarborImageConfig)
#
#
# @dataclasses.dataclass(frozen=True)
# class HarborScanOverviewSummaryComponent:
#     severity: int
#     count: int
#
#
# HarborScanOverviewSummaryComponentSchema = marshmallow_dataclass.class_schema(HarborScanOverviewSummaryComponent)
#
#
# @dataclasses.dataclass(frozen=True)
# class HarborScanOverviewComponents:
#     total: int
#     summary: typing.List[HarborScanOverviewSummaryComponent]
#
#
# HarborScanOverviewComponentsSchema = marshmallow_dataclass.class_schema(HarborScanOverviewComponents)
#
#
# @dataclasses.dataclass(frozen=True)
# class HarborScanOverview:
#     image_digest: str
#     scan_status: HarborImageScanStatus
#     job_id: int
#     severity: int
#     components: HarborScanOverviewComponents
#     details_key: str
#     creation_time: str
#     update_time: str
#
#
# HarborScanOverviewSchema = marshmallow_dataclass.class_schema(HarborScanOverview)
#
#
# @dataclasses.dataclass(frozen=True)
# class HarborImageTag:
#     digest: str  #
#     name: str #
#     size: int #
#     architecture: Architecture #
#     os: OS #
#     os_version: typing.Optional[str] = dataclasses.field(metadata={'data_key': 'os.version'})
#     docker_version: str #
#     author: str  #
#     created: str#
#     config: typing.Optional[HarborImageConfig]
#     signature: typing.Optional[str] #
#     scan_overview: typing.Optional[HarborScanOverview] #
#     labels: typing.List[str] #
#     push_time: str #
#     pull_time: str #
#     immutable: bool #
#
#
# HarborImageTagSchema = marshmallow_dataclass.class_schema(HarborImageTag)
#
#
# @dataclasses.dataclass(frozen=True)
# class Vulnerability:
#     id: str
#     severity: int
#     package: str
#     version: str
#     description: str
#     link: str
#     fixedVersion: str
#
#
# VulnerabilitySchema = marshmallow_dataclass.class_schema(Vulnerability)
#
#
# @dataclasses.dataclass(frozen=True)
# class HealthStatus:
#     name: str
#     status: HarborComponentHealthStatus
#     error: typing.Optional[str]
#
#
# @dataclasses.dataclass(frozen=True)
# class Health:
#     status: HarborComponentHealthStatus
#     components: typing.List[HealthStatus]
#
#     @property
#     def healthy(self) -> bool:
#         return self.status is HarborComponentHealthStatus.healthy
#
#
# HealthSchema = marshmallow_dataclass.class_schema(Health)
#
#
# @uplink.headers({"Accept": "application/json"})
# @uplink.response_handler(handler.raise_for_status)
# class Harbor(uplink.Consumer):
#     """A Simple client for the Harbor REST API"""
#
#     @uplink.get("/api/projects")
#     def get_projects(self) -> HarborProjectSchema(many=True):
#         """Lists all Harbor projects."""
#
#     @uplink.get("/api/repositories")
#     def get_repositories(self, project_id: uplink.Query) -> HarborRepositorySchema(many=True):
#         """Lists all repositories of a specified project"""
#
#     @uplink.get("/api/repositories/{repo_name}/tags/{tag}/manifest")
#     def get_manifest(self, repo_name: uplink.Path, tag: uplink.Path) -> ManifestResponseSchema:
#         """Returns the Manifest for a specified repository"""
#
#     @uplink.get("/api/projects/{project_id}/metadatas")
#     def get_metadatas(self, project_id: uplink.Path) -> HarborProjectMetadataSchema:
#         """Return the projects metadata"""
#
#     @uplink.get('/api/repositories/{repo_name}/tags')
#     def get_tags(self, repo_name: uplink.Path) -> HarborImageTagSchema(many=True):
#         """Returns the tags for a particular repository"""
#
#     @uplink.get("/api/repositories/{repo_name}/tags/{tag}/vulnerability/details")
#     def get_vulnerabilities(self, repo_name: uplink.Path, tag: uplink.Path) -> VulnerabilitySchema(many=True):
#         """Returns the vulnerabilities of a particular image"""
#
#     @uplink.get("/api/health")
#     def get_health(self) -> HealthSchema:
#         """Returns Health of  Harbor instance"""
