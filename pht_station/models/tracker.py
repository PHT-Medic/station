import dataclasses

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr


from pht_trainlib.util import timestamp_now
from pht_station.db_util import provide_session
from .internal import Base


@dataclasses.dataclass(frozen=True)
class TrackerView:
    tracker_id: int
    repository: str
    tag: str

#
# @dataclasses.dataclass(frozen=True)
# class TrackerIdentityView:
#     tracker_identity_id: int
#     revision: int
#     docker_image_config_id: int
#     docker_image_manifest_id: int
#     identity_data: str
#     failed_at: str
#     tracker: TrackerView


class Tracker(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    repository = sa.Column(sa.String(80), unique=False, nullable=False)
    tag = sa.Column(sa.String(80), unique=False, nullable=False)
    created_at = sa.Column(sa.DateTime, unique=False, nullable=False, default=timestamp_now)

    @classmethod
    @provide_session
    def upsert(cls, repository: str, tag: str, session=None) -> TrackerView:
        """Returns a tracker for the repository and tag and raises AlreadyExistsException if such a
        tracker is already present"""
        existing = session.query(cls).filter_by(repository=repository, tag=tag).first()
        if existing:
            tracker = existing
        else:
            tracker = Tracker(repository=repository, tag=tag)
            session.add(tracker)
            session.commit()
        return TrackerView(
            tracker_id=tracker.id,
            repository=tracker.repository,
            tag=tracker.tag)


class TrackerIdentity(Base):

    @declared_attr
    def __tablename__(cls):
        return 'tracker_identity'

    id = sa.Column(sa.Integer, primary_key=True)
    tracker_id = sa.Column(sa.Integer, sa.ForeignKey('tracker.id'), unique=False, nullable=False)

    # The n-th identity of this tracker
    revision = sa.Column(sa.Integer, unique=False, nullable=False)

    # Columns that make up the identity
    docker_image_manifest_id = sa.Column(sa.Integer, sa.ForeignKey('docker_image_manifest.id'),
                                         unique=False, nullable=False)
    digest_tag_harbor = sa.Column(sa.String(80), unique=False, nullable=False)

    # Metadata that is associated with this identity
    identity_data = sa.Column(sa.JSON, unique=False, nullable=True)

    # when this identity was created
    created_at = sa.Column(sa.DateTime, unique=False, nullable=False, default=timestamp_now)

    @classmethod
    @provide_session
    def upsert(cls,
               tracker_id: int,
               docker_image_manifest_id: int,
               digest_tag_harbor: str,
               session=None) -> int:
        existing = session.query(cls).filter_by(
            docker_image_manifest_id=docker_image_manifest_id,
            tracker_id=tracker_id,
            digest_tag_harbor=digest_tag_harbor).first()

        if existing:
            result = existing.id
        else:
            t = TrackerIdentity(
                tracker_id=tracker_id,
                revision=0,  # TODO Revisions currently not supported
                docker_image_manifest_id=docker_image_manifest_id,
                digest_tag_harbor=digest_tag_harbor)
            session.add(t)
            session.commit()
            result = t.id
        return result

    # @classmethod
    # @provide_session
    # def view(cls, tracker_identity_id: int, session=None) -> TrackerIdentityView:
    #     """Returns the view of the Tracker Identity"""
    #     existing = session.query(cls).get(tracker_identity_id)
    #     if not existing:
    #         raise NotFoundException(f'Tracker Identity with the ID {tracker_identity_id} does not exist!')
    #     tracker = existing.tracker
    #     return TrackerIdentityView(
    #         tracker_identity_id=tracker_identity_id,
    #         revision=existing.revision,
    #         docker_image_config_id=existing.docker_image_config_id,
    #         docker_image_manifest_id=existing.docker_image_manifest_id,
    #         identity_data=existing.identity_data,
    #         failed_at=existing.failed_at,
    #         tracker=TrackerView(
    #             tracker_id=tracker.id,
    #             repository=tracker.repository,
    #             tag=tracker.tag))
