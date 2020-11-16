from airflow.hooks.http_hook import HttpHook


class HarborHook(HttpHook):
    def __init__(self, method='GET', http_conn_id='harbor_conn'):
        super().__init__(method, http_conn_id)

    def get_conn(self, headers=None):
        return super().get_conn(headers)
