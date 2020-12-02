import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from .internal import Base
from pht_station.airflow_plugin.db_util import provide_session

_STATE_CREATED = 1


class ProcessingState(Base):
    @declared_attr
    def __tablename__(cls):
        return 'processing_state'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(80), unique=True, nullable=False)


class Processing(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    processing_state_id = sa.Column(sa.Integer, sa.ForeignKey('processing_state.id'),
                                    unique=False, nullable=False)
    tracker_identity_id = sa.Column(sa.Integer, sa.ForeignKey('tracker_identity.id'),
                                    unique=False, nullable=False)

    @classmethod
    @provide_session
    def create(cls, tracker_identity_id: int, session=None) -> int:
        proc = Processing(processing_state_id=_STATE_CREATED, tracker_identity_id=tracker_identity_id)
        session.add(proc)
        session.commit()
        return proc.id

