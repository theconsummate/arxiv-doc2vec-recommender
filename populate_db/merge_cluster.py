from pymongo import MongoClient
import pymongo.errors as pyerror

master_db = 'patent'
clusters = ['pa', 'pb', 'pc', 'pd', 'pe', 'pf', 'pg', 'ph']
collection_name = 'patents'

db = MongoClient()[master_db]['patents']
for cluster in clusters:
    cluster_db = MongoClient()[cluster]['patents']
    items = cluster_db.find()
    for item in items:
        try:
            db.insert_one(item)
        except pyerror.DuplicateKeyError:
            pass


