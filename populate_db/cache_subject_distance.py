import pickle
import pandas as pd
import gensim
from gensim.models.doc2vec import Doc2Vec
import numpy as np
from scipy.spatial.distance import pdist, squareform
from pymongo import MongoClient
import sys


"""
Note: You have to have ran cache_subject_hash.py before
running this script.

This produces a CSV file that d3 looks for
to create a visualization of topics and their
distances.

We first calculate the average vector of articles per subject,
Then calculate the pairwise distance of these topic vectors,
and lastly produce a CSV that relates the n closest topics,
with one relationship per row.
"""

def get_category_hash(db):
    """
    INPUT: (str) name of database containing the subjects table.
    NOTE: The subject table is produces by cache_subject_hash.py
    which must be run first
    OUTPUT: (dict) {subject_id: subject_name}
    """
    # add cpc description here later
    results = db.distinct('_cpc_category')
    subject_hash = {i: i for i in results}
    return subject_hash

def get_category_vectors(category_hash, db, model):
    """
    Get panda DataFrame where each row is a subject's average docvec
    and index is the subject_id
    """
    category_vectors = {}
    for category_id in category_hash.keys():
        # for cpc_id in category_hash[category_id]:
        # article_vectors = np.array([model.docvecs[id['_id']] for cpc_id in category_hash[category_id] for id in db['patents'].find({"_cpc":cpc_id}, {"_id":1})])
        article_vectors = np.array([model.docvecs[id['_id']] for id in db.find({"_cpc_category":category_id}, {"_id":1})])
        print len(article_vectors)
        category_vectors[category_id] = np.mean(article_vectors, axis=0)
    # turn the dictionary into a dataframe and return
    return category_vectors

def get_distance_mat(cpc_vectors, dist='cosine'):
    """
    returns pandas dataframe where indices and col_names
    are cpc_ids, and each cell (i,j) is the distance between
    the subjects (i,j)
    """
    # dense matrix of distance pairs between subject vectors
    Y = squareform(pdist(cpc_vectors, dist))
    # transfer cpc_ids as index to Y:
    distance_mat = pd.DataFrame(Y, index=cpc_vectors.index, columns=cpc_vectors.index)
    return distance_mat

def get_n_closest(distance_mat, subject_id, n=5):
    """
    Sorts a distance matrix's column for a particular subject and returns
    n closest cpc_ids
    """
    s = distance_mat.loc[subject_id]
    closest = s.sort_values()[1:1+n]
    return closest


def get_category_vectors_all_db(db, model):
    dbs_list = ['pa', 'pb', 'pc', 'pd', 'pe', 'pf', 'pg', 'ph']
    cpc_vectors = {}
    category_ids = []
    for database in dbs_list:
        category_hash = get_category_hash(db[database]['patents'])
        category_ids += list(category_hash.keys())
        # loop over subjects and average docvecs belonging to subject.
        # place in dictionary
        cpc_vectors_single_db = get_category_vectors(category_hash, db[database]['patents'], model)
        cpc_vectors.update(cpc_vectors_single_db)
    return pd.DataFrame(cpc_vectors).T, category_ids


def get_category_vectors_subset(model, category_hash_with_doc_ids):
    """
    Get panda DataFrame where each row is a subject's average docvec
    and index is the subject_id
    """
    category_vectors = {}
    for category_id in category_hash_with_doc_ids.keys():
        article_vectors = []
        for id in category_hash_with_doc_ids[category_id]:
            try:
                article_vectors.append(np.array(model.docvecs[id]))
            except KeyError:
                pass
        category_vectors[category_id] = np.mean(article_vectors, axis=0)
    # turn the dictionary into a dataframe and return
    return pd.DataFrame(category_vectors).T

def get_distances(db, model, n_closest):
    # loop over subjects and average docvecs belonging to subject.
    # place in dictionary
    cpc_vectors, category_ids = get_category_vectors_all_db(db, model)
    distance_mat = get_distance_mat(cpc_vectors)

    to_csv = []
    for subj_id in category_ids:
        relateds = get_n_closest(distance_mat, subj_id, n=n_closest)
        for related_id, dist in relateds.iteritems():
            weight = round(1./dist)
            #weight = round((1-dist) * 10)
            row = (subj_id, related_id, weight, subj_id, related_id)
            to_csv.append(row)

    edges = pd.DataFrame(to_csv, columns=['source', 'target', 'weight', 'source_name', 'target_name'])
    edges.to_csv('../static/subject_distances.csv', index=False)

def get_distances_subset(n_closest, category_hash_with_doc_ids, csv_path):
    # example
    # category_hash_with_doc_ids = {"cat1":["us-1", "us-2"], "cat2": ["us-3"]}
    # loop over subjects and average docvecs belonging to subject.
    # place in dictionary
    model = Doc2Vec.load('../doc2vec_model')
    cpc_vectors  = get_category_vectors_subset(model, category_hash_with_doc_ids)
    distance_mat = get_distance_mat(cpc_vectors)

    to_csv = []
    for subj_id in list(category_hash_with_doc_ids.keys()):
        relateds = get_n_closest(distance_mat, subj_id, n=n_closest)
        for related_id, dist in relateds.iteritems():
            weight = round(1./dist)
            #weight = round((1-dist) * 10)
            row = (subj_id, related_id, weight, subj_id, related_id)
            to_csv.append(row)

    edges = pd.DataFrame(to_csv, columns=['source', 'target', 'weight', 'source_name', 'target_name'])
    edges.to_csv(csv_path, index=False)

if __name__ == '__main__':
    print "main"
    model = Doc2Vec.load('../doc2vec_model')
    # db = MongoClient()
    # get_distances(db, model, int(sys.argv[1]))
    get_distances_subset(model, 5, data, '../static/subject_distances1.csv')


