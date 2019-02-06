from flask_login import UserMixin
from pony.orm import db_session

from database.dbinit import WebUser


class FlaskUser(UserMixin):
    def __init__(self, username):
        self.username = username
        with db_session:
            self.username = username
            self.webuser = WebUser[username]
            self.is_admin = self.webuser.is_admin

    def get_id(self):
        return self.webuser.username

    @property
    def is_active(self):
        return self.webuser.is_active
