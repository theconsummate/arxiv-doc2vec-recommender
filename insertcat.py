from pymongo import MongoClient

file = open('cpc_code.csv')
json = {}
for row in file.readlines():
    code, cat = row.strip().split(',')
    if cat in json.keys():
        json[cat].append(code)
    else:
        json[cat] = [code]
print json

db = MongoClient()['patent']
for key in json.keys():
    db['categories'].insert_one({"cat_code": key, "cpc_code" : json[key]})
