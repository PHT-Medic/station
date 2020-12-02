# import json
# import typing
#
# from airflow.hooks.base_hook import BaseHook
#
#
# import pht_trainlib.util as util
# from pht_station import TrackerIdentity
#
#
# # TODO This is just a hack
#
#
# def create_image_name(context) -> typing.Tuple[str, str, str]:
#     """
#     From the context provided to the DAG and the host of the registry and returns:
#     (repo_without_tag, repo_with_tag, tag)
#     """
#     registry_host = util.without_suffix(
#         BaseHook.get_connection('pht_station_all_docker_container_registry').host,
#         suffix='/')
#
#     tracker = context['params']['tracker_identity']['tracker']
#
#     repo = util.without_suffix(tracker['repository'], suffix=':')
#     tag = util.without_prefix(tracker['tag'], prefix=':')
#
#     repo = registry_host + '/' + repo
#     return repo, repo + ':' + tag, tag
#
#
# def get_tracker_identity_id(context) -> int:
#     return int(context['params']['tracker_identity']['id'])
#
#
# def set_inspection(tracker_identity_id, inspection):
#     TrackerIdentity.update_data(tracker_identity_id=tracker_identity_id, data={
#         'inspection': json.loads(inspection)
#     })
#
#
