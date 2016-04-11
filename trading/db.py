import os

from bson import ObjectId
from pymongo import ReadPreference, MongoClient


def create_ds_mongo_client(read_preference):
    hosts = os.environ['MONGODB_HOSTS']
    mongo = MongoClient(hosts, read_preference=read_preference)
    if 'MONGODB_NO_AUTH' not in os.environ:
        user = os.environ['MONGODB_USER']
        password = os.environ['MONGODB_PASSWORD']
        mongo.admin.authenticate(user, password)
    return mongo


def get_database(read_preference=ReadPreference.SECONDARY_PREFERRED):
    mongo = create_ds_mongo_client(read_preference=read_preference)
    return mongo.model_gym


def transform_son(son):
    for field in son:
        if isinstance(son[field], dict):
            transform_son(son[field])
        elif isinstance(son[field], ObjectId):
            son[field] = str(son[field])
            if field == '_id':
                son['id'] = son.pop('_id')
    return son
