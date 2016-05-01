# -*- coding: utf-8 -*-
from pymongo import MongoClient
from flask import Flask, render_template, request, url_for
from gensim.models import Doc2Vec
from populate_db import cache_subject_distance as distances

app = Flask(__name__)

@app.route('/')
def viz():
    n = request.args.get('n')
    if n == None:
        n = 5
    distances.get_distances(db, model, n)
    csv_dest = url_for('static', filename='subject_distances.csv')
    return render_template("louvain.html", csv_dest=csv_dest)

if __name__ == '__main__':
    # run app in db connection context
    db = MongoClient()['patent']
    # load model:
    model = Doc2Vec.load('./doc2vec_model')
    app.run(host='0.0.0.0', port=5000)
