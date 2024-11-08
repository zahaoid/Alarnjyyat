from flask_login import UserMixin




class User(UserMixin):

    def __init__(self, username, isadmin) -> None:
        super().__init__()
        self.username = username
        self.isadmin = isadmin

    #according to the documentation, this must returns a string (and obviously for each user unique) value
    def get_id(self):
        return self.username
    