"""Create 0.1.0 tables

Revision ID: 0956d9e54221
Revises: 
Create Date: 2020-02-12 11:00:00.048364

"""
import datetime

import alembic
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0956d9e54221'
down_revision = None
branch_labels = None
depends_on = None

# TODO Maybe namespaces?
# Table names
# _table_resource_type = 'resource_type'
# _table_resource = 'resource'
_table_media_type = 'media_type'
_table_hash_value_sha256 = 'hash_value_sha256'
_table_docker_image_manifest = 'docker_image_manifest'
_table_docker_image_manifest_layer = 'docker_image_manifest_layer'
_table_tracker = 'tracker'
_table_tracker_identity = 'tracker_identity'
_table_processing_state = 'processing_state'
_table_processing = 'processing'


def upgrade():

    # Column values
    created_at = datetime.datetime.now(datetime.timezone.utc)

    # Column names
    _id = 'id'
    _name = 'name'
    _value = 'value'
    _attribute_descriptions = 'attribute_descriptions'
    _created_at = 'created_at'
    _order = 'order'
    _digest = 'digest'

    # Table: resource_type
    # table = alembic.op.create_table(
    #     _table_resource_type,
    #     sa.Column(_id, sa.Integer, primary_key=True),
    #     sa.Column(_name, sa.String(40), unique=True, nullable=False),
    #
    #     # Stores attributes names to their descriptions
    #     sa.Column(_attribute_descriptions, sa.JSON, nullable=True, unique=False))
    #
    # alembic.op.bulk_insert(table, [{
    #     _name: 'DOCKER_VOLUME',
    #     _attribute_descriptions: {
    #         _name: 'The name of the Docker volume as reported by the docker daemon'
    #     }
    # }])

    # Table: resource
    # alembic.op.create_table(
    #     _table_resource,
    #     sa.Column('id', sa.Integer, primary_key=True),
    #     sa.Column('key', sa.String(80), unique=True, nullable=False),
    #     sa.Column('resource_type_id', sa.Integer, sa.ForeignKey('resource_type.id'), unique=False, nullable=False),
    #
    #     # The resource-specific attributes
    #     sa.Column('attributes', sa.JSON, unique=False, nullable=False),
    #
    #     # Configuration for resource attached to container at runtime
    #     sa.Column('container_config', sa.JSON, unique=False, nullable=True))

    # Table: media_type
    table = alembic.op.create_table(
        _table_media_type,
        sa.Column(_id, sa.Integer, primary_key=True),
        sa.Column(_value, sa.String(length=80), unique=True, nullable=False),
        sa.Column(_created_at, sa.DateTime, unique=False, nullable=False))

    alembic.op.bulk_insert(table, [
        {
            _value: 'application/vnd.docker.distribution.manifest.v2+json',
            _created_at: created_at
        }, {
            _value: 'application/vnd.docker.image.rootfs.diff.tar.gzip',
            _created_at: created_at
        }, {
            _value: 'application/vnd.docker.container.image.v1+json',
            _created_at: created_at
        }
    ])

    # Table: hash_value_sha256
    alembic.op.create_table(
        _table_hash_value_sha256,
        sa.Column(_id, sa.Integer, primary_key=True),
        sa.Column(_value, sa.Binary(length=32), unique=True, nullable=False),
        sa.Column(_created_at, sa.DateTime, unique=False, nullable=False))

    # Table: docker_image_manifest
    alembic.op.create_table(
        _table_docker_image_manifest,
        sa.Column(_id, sa.Integer,  primary_key=True),
        sa.Column('schema_version', sa.SmallInteger, unique=False, nullable=False),
        sa.Column('media_type', sa.Integer, sa.ForeignKey('media_type.id'), unique=False, nullable=False),
        sa.Column('config_media_type', sa.Integer, sa.ForeignKey('media_type.id'), unique=False, nullable=False),
        sa.Column('config_size', sa.Integer, unique=False, nullable=False),
        sa.Column('config_digest', sa.Integer, sa.ForeignKey('hash_value_sha256.id'), unique=True, nullable=False),
        sa.Column(_created_at, sa.DateTime, unique=False, nullable=False))

    # Table: docker_image_manifest_layer
    alembic.op.create_table(
        _table_docker_image_manifest_layer,
        sa.Column('docker_image_manifest_id', sa.Integer, sa.ForeignKey('docker_image_manifest.id'), primary_key=True),
        sa.Column(_order, sa.SmallInteger, primary_key=True),
        sa.Column('media_type', sa.Integer, sa.ForeignKey('media_type.id'), unique=False, nullable=False),
        sa.Column('size', sa.Integer, unique=False, nullable=False),
        sa.Column(_digest, sa.Integer, sa.ForeignKey('hash_value_sha256.id'), unique=False, nullable=False),
        sa.Column(_created_at, sa.DateTime, unique=False, nullable=False))

    # Table: tracker
    alembic.op.create_table(
        _table_tracker,
        sa.Column(_id, sa.Integer, primary_key=True),
        sa.Column('repository', sa.String(80), unique=False, nullable=False),
        sa.Column('tag', sa.String(80), unique=False, nullable=False),
        sa.Column(_created_at, sa.DateTime, unique=False, nullable=False))

    # Table: tracker_identity
    alembic.op.create_table(
        _table_tracker_identity,
        sa.Column(_id, sa.Integer, primary_key=True),
        sa.Column('tracker_id', sa.Integer, sa.ForeignKey('tracker.id'), unique=False, nullable=False),

        # The n-th identity of this tracker
        sa.Column('revision', sa.Integer, unique=False, nullable=False),

        # Columns that make up the identity
        sa.Column('docker_image_manifest_id', sa.Integer, sa.ForeignKey('docker_image_manifest.id'),
                  unique=False, nullable=False),

        # TODO v0.2.0 foreign key to sha256 table
        sa.Column('digest_tag_harbor', sa.String(80), unique=False, nullable=False),

        # Metadata that is associated with this identity
        sa.Column('identity_data', sa.JSON, unique=False, nullable=True),

        # when this identity was created
        sa.Column(_created_at, sa.DateTime, unique=False, nullable=False))

    # Table: processing_state
    table = alembic.op.create_table(
        _table_processing_state,
        sa.Column(_id, sa.Integer, primary_key=True),
        sa.Column(_name, sa.String(80), unique=True, nullable=False))

    alembic.op.bulk_insert(table, [
        {
            _name: 'Created',
        }, {
            _name: 'Running',
        }, {
            _name: 'Success'
        }
    ])

    # Table: processing
    alembic.op.create_table(
        _table_processing,
        sa.Column(_id, sa.Integer, primary_key=True),
        sa.Column('processing_state_id', sa.Integer, sa.ForeignKey('processing_state.id'),
                  unique=False, nullable=False),
        sa.Column('tracker_identity_id', sa.Integer, sa.ForeignKey('tracker_identity.id'),
                  unique=False, nullable=False))


def downgrade():
    # Drop tables in reverse order of creation
    alembic.op.drop_table(_table_processing)
    alembic.op.drop_table(_table_processing_state)
    alembic.op.drop_table(_table_tracker_identity)
    alembic.op.drop_table(_table_tracker)
    alembic.op.drop_table(_table_docker_image_manifest_layer)
    alembic.op.drop_table(_table_docker_image_manifest)
    alembic.op.drop_table(_table_hash_value_sha256)
    alembic.op.drop_table(_table_media_type)
    # alembic.op.drop_table(_table_resource)
    # alembic.op.drop_table(_table_resource_type)
