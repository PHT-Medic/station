import typing

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from pht_station.airflow_plugin.db_util import provide_session
from .internal import Base


class MediaType(Base):
    @declared_attr
    def __tablename__(cls):
        return 'media_type'

    id = sa.Column(sa.Integer, primary_key=True)
    value = sa.Column(sa.String(length=80), unique=True, nullable=False)
    created_at = sa.Column(sa.DateTime, unique=False, nullable=False)

    @classmethod
    @provide_session
    def get_primary_keys(cls, values: typing.Iterable[str], session=None) -> typing.Iterable[int]:
        media_types = {
            mt.value: mt for mt in session.query(cls).all()
        }
        return [media_types[value].id for value in values]
