import config

from pymongo import MongoClient


class MongoConnection:
    connection = config.DATABASE_CONFIG['url']
    db = config.DATABASE_CONFIG['db_name']
