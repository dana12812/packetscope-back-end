# data/tag_data.py — test tags, attached to a user in seed.py.

from models.tag import TagModel


def create_test_tags(user):
    return [
        TagModel(name="work", color="#0F766E", user=user),
        TagModel(name="home lab", color="#B45309", user=user),
        TagModel(name="suspicious", color="#4338CA", user=user),
    ]