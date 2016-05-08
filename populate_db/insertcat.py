from pymongo import MongoClient
import pymongo.errors as pyerror

file = open('../cpc_code.csv')
json = {}
for row in file.readlines():
    code, cat = row.strip().split(',')
    if cat == '':
        continue
    elif cat in json.keys():
        json[cat].append(code)
    else:
        json[cat] = [code]
print json

db = MongoClient()['patent']
for key in json.keys():
    try:
        db['categories'].insert_one({"cat_code": key, "cpc_code" : json[key]})
    except pyerror.DuplicateKeyError:
        print "inserting duplicate"
