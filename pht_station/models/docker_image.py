import dataclasses
import typing

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy.orm

from pht_trainlib.util import timestamp_now
from pht_station.airflow_plugin.db_util import provide_session
from .internal import Base


@dataclasses.dataclass(frozen=True)
class ImageManifestSkeleton:
    """Represents an DockerImage Manifest, where mediaTypes and digests
     are represented by the primary keys of these objects in the database.
    """
    schemaVersion: int
    mediaType: int
    config_media_type: int
    config_size: int
    config_digest: int
    layer_media_types: typing.List[int]
    layer_sizes: typing.List[int]
    layer_digests: typing.List[int]


class DockerImageManifest(Base):

    @declared_attr
    def __tablename__(cls):
        return 'docker_image_manifest'

    id = sa.Column(sa.Integer, primary_key=True)
    schema_version = sa.Column(sa.SmallInteger, unique=False, nullable=False)
    media_type = sa.Column(sa.Integer, sa.ForeignKey('media_type.id'), unique=False, nullable=False)
    config_media_type = sa.Column(sa.Integer, sa.ForeignKey('media_type.id'), unique=False, nullable=False)
    config_size = sa.Column(sa.Integer, unique=False, nullable=False)
    config_digest = sa.Column(sa.Integer, sa.ForeignKey('hash_value_sha256.id'), unique=True, nullable=False)
    created_at = sa.Column(sa.DateTime, unique=False, nullable=False, default=timestamp_now)

    layers = sqlalchemy.orm.relationship('DockerImageManifestLayer')

    @classmethod
    @provide_session
    def insert(cls, manifest_skel: ImageManifestSkeleton, session=None) -> int:
        """Inserts manifest via Skeleton and returns primary key"""
        m = manifest_skel
        existing = session.query(cls).filter_by(config_digest=m.config_digest).first()
        if not existing:
            manifest = DockerImageManifest(
                schema_version=m.schemaVersion,
                media_type=m.mediaType,
                config_media_type=m.config_media_type,
                config_size=m.config_size,
                config_digest=m.config_digest)
            manifest.layers = [
                DockerImageManifestLayer(order=order, media_type=media_type, size=size, digest=digest)
                for (order, (media_type, size, digest))
                in enumerate(zip(m.layer_media_types, m.layer_sizes, m.layer_digests))
            ]
            session.add(manifest)
            session.commit()
            result = manifest.id
        else:
            result = existing.id
        return result


class DockerImageManifestLayer(Base):

    @declared_attr
    def __tablename__(cls):
        return 'docker_image_manifest_layer'

    docker_image_manifest_id = sa.Column(sa.Integer, sa.ForeignKey('docker_image_manifest.id'), primary_key=True)
    order = sa.Column(sa.SmallInteger, primary_key=True)
    media_type = sa.Column( sa.Integer, sa.ForeignKey('media_type.id'), unique=False, nullable=False)
    size = sa.Column(sa.Integer, unique=False, nullable=False)
    digest = sa.Column(sa.Integer, sa.ForeignKey('hash_value_sha256.id'), unique=False, nullable=False)
    created_at = sa.Column(sa.DateTime, unique=False, nullable=False, default=timestamp_now)
