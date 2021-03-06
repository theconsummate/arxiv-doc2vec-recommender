# -*- coding: utf-8 -*-
from pymongo import MongoClient
from flask import Flask, render_template, request, url_for, redirect
# from gensim.models import Doc2Vec
from populate_db import cache_subject_distance as distances
from datetime import datetime

app = Flask(__name__)
# app.debug = True

def get_dict_from_ids(ids):
    cats = {}
    db = MongoClient()['patent']['patents']
    for id in ids:
        item = db.find_one({"_id":id}, {"_id":1, "_cpc_category":1})
        if item == None:
            continue
        if item["_cpc_category"] in cats.keys():
            cats[item["_cpc_category"]].append(item["_id"])
        else:
            cats[item["_cpc_category"]] = [item["_id"]]
    return cats

@app.route('/')
def viz():
    csv_dest = url_for('static', filename='subject_distances.csv')
    return render_template("louvain.html", csv_dest=csv_dest)


@app.route('/query', methods=['POST'])
def get_subset():
    # /var/www/html/flaskapp/static/
    if request.method == 'POST':
        # ids = request.get_json(force=True)['patents']
        ids = request.form.getlist('patent')
        data = get_dict_from_ids(ids)
        if not bool(data):
            return redirect(url_for('viz_nodata'), code=302)
        distances.get_distances_subset(5, data, '/var/www/html/flaskapp/static/subject_distances2.csv')
        print "done generating."
        # csv_dest = url_for('static', filename='subject_distances1.csv')
        return redirect(url_for('viz_subset') + '?timestamp='+datetime.now().strftime('%H%M%S%f'), code=302)


@app.route('/nodata', methods=['GET', 'POST'])
def viz_nodata():
    return "No data found for that search term."


@app.route('/viz', methods=['GET', 'POST'])
def viz_subset():
    csv_dest = url_for('static', filename='subject_distances2.csv')
    return render_template("louvain.html", csv_dest=csv_dest)


if __name__ == '__main__':
    # run app in db connection context
    # db = MongoClient()['patent']
    # load model:
    # model = Doc2Vec.load('./doc2vec_model')
    app.run(host='0.0.0.0', port=5000)
