from flask_admin import BaseView, expose

from .internal import template_path


_template_running_trains = template_path('running_trains')


class RunningTrains(BaseView):

    ###############################################################
    # Views
    ###############################################################
    @expose('/')
    def running_trains(self):
        return self.render(_template_running_trains)
