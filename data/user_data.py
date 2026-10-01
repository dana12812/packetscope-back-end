# data/user_data.py — test users for seeding.
from models.user import UserModel


def create_test_users():
    user1 = UserModel(username="dana", email="dana@example.com")
    user1.set_password("123")
    user2 = UserModel(username="test_user", email="test@example.com")
    user2.set_password("123")
    return [user1, user2]


user_list = create_test_users()