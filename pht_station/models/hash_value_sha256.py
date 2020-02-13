import typing

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from pht_trainlib.util import timestamp_now

from pht_station.db_util import open_session
from .internal import Base


class HashValueSHA256(Base):
    @declared_attr
    def __tablename__(cls):
        return 'hash_value_sha256'

    id = sa.Column(sa.Integer, primary_key=True)
    value = sa.Column(sa.Binary(length=32), unique=True, nullable=False)
    created_at = sa.Column(sa.DateTime, unique=False, nullable=False, default=timestamp_now)

    @classmethod
    def upsert_all(cls, values: typing.Iterable[str]) -> typing.Sequence[int]:
        values = [_load_sha256(s) for s in values]
        result = []
        new_values = []
        with open_session() as session:
            existing = {
                value.value: value for value in session.query(cls).filter(HashValueSHA256.value.in_(values)).all()
            }
            for value in values:
                if value in existing:
                    result_value = existing[value]
                else:
                    result_value = HashValueSHA256(value=value)
                    new_values.append(result_value)
                result.append(result_value)

            session.add_all(new_values)
            session.commit()
            return [value.id for value in result]


_SHA256_PREFIX = 'sha256:'
_SHA256_PREFIX_LEN = len(_SHA256_PREFIX)
_SHA256_N_BYTES = 32


def _load_sha256(s: str) -> bytes:
    if not s.startswith(_SHA256_PREFIX):
        raise ValueError('Cannot convert str to sha256 bytes!')
    result = bytes.fromhex(s[_SHA256_PREFIX_LEN:])
    n_bytes = len(result)
    if n_bytes != _SHA256_N_BYTES:
        raise ValueError(f'Number of bytes of value {n_bytes} does not match the expected number:'
                         f' {_SHA256_N_BYTES} for sha256!')
    return result
