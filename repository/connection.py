import config

from pymongo import MongoClient


class MongoConnection:
    connection = MongoClient(config.DATABASE_CONFIG['url'])
    db = connection[config.DATABASE_CONFIG['db_name']]
