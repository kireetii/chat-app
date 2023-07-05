from werkzeug.security import check_password_hash

class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.name

    def verify_password(self, password_input):
        return check_password_hash(self.password, password_input)