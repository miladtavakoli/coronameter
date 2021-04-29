from pymongo import MongoClient


class MongoConnection:
    connection = MongoClient('mongodb://localhost:27017/')
    db = connection['worldometers']
