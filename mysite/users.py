from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def convert_to_user_obj(user_data):
        user = User(
            id_=user_data['unique_id'], name=user_data['users_name'], email=user_data['users_email'], profile_pic=user_data['picture']
        )
        return user