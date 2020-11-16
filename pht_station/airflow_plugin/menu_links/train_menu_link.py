from flask_admin.base import MenuLink


class TrainMenuLink(MenuLink):
    def __init__(self, name, url=None, endpoint=None, category=None, class_name=None, icon_type=None, icon_value=None,
                 target=None):
        super().__init__(name, url, endpoint, category, class_name, icon_type, icon_value, target)
