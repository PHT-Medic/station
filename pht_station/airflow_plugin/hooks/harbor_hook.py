from airflow.hooks.http_hook import HttpHook


class HarborHook(HttpHook):
    def __init__(self, method='POST', http_conn_id='http_default'):
        super().__init__(method, http_conn_id)

    def get_conn(self, headers=None):
        return super().get_conn(headers)
