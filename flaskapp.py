# -*- coding: utf-8 -*-
from pymongo import MongoClient
from flask import Flask, render_template, request, url_for
# from gensim.models import Doc2Vec
from populate_db import cache_subject_distance as distances

app = Flask(__name__)

def get_dict():
    clusters = ['pa', 'pb', 'pc', 'pd', 'pe', 'pf', 'pg', 'ph']
    cats = {}
    for cluster in clusters:
        cluster_db = MongoClient()[cluster]['patents']
        items = cluster_db.find({}, {"_id":1, "_cpc_category":1}).limit(500)
        for item in items:
            if item["_cpc_category"] in cats.keys():
                cats[item["_cpc_category"]].append(item["_id"])
            else:
                cats[item["_cpc_category"]] = [item["_id"]]
    return cats

@app.route('/')
def viz():
    csv_dest = url_for('static', filename='subject_distances.csv')
    return render_template("louvain.html", csv_dest=csv_dest)


@app.route('/query')
def viz():
    distances.get_distances_subset(5, get_dict(), './static/subject_distances1.csv')
    print "done generating."
    csv_dest = url_for('static', filename='subject_distances1.csv')
    return render_template("louvain.html", csv_dest=csv_dest)

if __name__ == '__main__':
    # run app in db connection context
    # db = MongoClient()['patent']
    # load model:
    # model = Doc2Vec.load('./doc2vec_model')
    app.run(host='0.0.0.0', port=5000)
