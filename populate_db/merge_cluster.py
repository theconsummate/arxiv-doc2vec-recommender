from pymongo import MongoClient
import pymongo.errors as pyerror

master_db = 'patent'
clusters = ['p0', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
collection_name = 'patents'

db = MongoClient()['patent']['patents']
for cluster in clusters:
    cluster_db = MongoClient()[cluster]['patents']
    items = cluster_db.find()
    for item in items:
        try:
            db.insert_one(item)
        except pyerror.DuplicateKeyError:
            pass


