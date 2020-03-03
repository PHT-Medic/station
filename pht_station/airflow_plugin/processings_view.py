from flask_admin import BaseView, expose

from .internal import template_path


_template_processings = template_path('processings')


class Processings(BaseView):

    ###############################################################
    # Views
    ###############################################################
    @expose('/')
    def processings(self):
        return self.render(_template_processings)
