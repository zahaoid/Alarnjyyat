from flask_login import UserMixin




class User(UserMixin):

    def __init__(self, username, isadmin) -> None:
        super().__init__()
        self.username = username
        self.isadmin = isadmin

    def get_id(self):
        return self.username
    