# import dataclasses
# import types
# import typing
#
# import sqlalchemy as sa
# from pht_station.airflow_plugin.models.db_util import provide_session
# from .. import Base
#
#
# @dataclasses.dataclass(frozen=True)
# class ResourceView:
#     id: int
#     key: str
#     resource_type_id: int
#     attributes: str
#     container_config: str
#
#
# class Resource(Base):
#     id = sa.Column(sa.Integer, primary_key=True)
#     key = sa.Column(sa.String(80), unique=True, nullable=False)
#     resource_type_id = sa.Column(sa.Integer, sa.ForeignKey('resource_type.id'), unique=False, nullable=False)
#
#     # The resource-specific attributes
#     attributes = sa.Column(sa.JSON, unique=False, nullable=False)
#
#     # Configuration for resource attached to container at runtime
#     container_config = sa.Column(sa.JSON, unique=False, nullable=False)
#
#     @classmethod
#     def _all(cls, session):
#         return session.query(cls).all()
#
#     @classmethod
#     @provide_session
#     def view_all(cls, session=None) -> typing.Iterable[ResourceView]:
#         return [
#             ResourceView(
#                 id=r.id,
#                 key=r.key,
#                 resource_type_id=r.resource_type_id,
#                 attributes=str(r.attributes),
#                 container_config=str(r.container_config)) for r in cls._all(session)
#         ]
#
#     @classmethod
#     @provide_session
#     def tabulate(cls, *,
#                  key_f,
#                  value_f,
#                  resource_type_id: typing.Optional[int] = None,
#                  session=None) -> typing.Mapping[typing.Any, typing.Any]:
#         resources = cls._all(session) if resource_type_id is None\
#             else session.query(cls).filter_by(resource_type_id=resource_type_id).all()
#         return types.MappingProxyType({
#             key_f(r): value_f(r) for r in resources
#         })
#
#     # @classmethod
#     # @provide_session
#     # def create(cls, session=None):
#     #     pass
