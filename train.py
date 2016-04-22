# -*- coding: utf-8 -*-
import multiprocessing
import psycopg2
from psycopg2.extras import DictCursor
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import re
import argparse
from pymongo import MongoClient


class DocIterator(object):
    """
    gensim documentation calls this "streaming a corpus", which
    lets us train without holding entire corpus in memory.
    It needs to be an object so gensim can make multiple passes over data.
    Here, we stream from a postgres database.
    """
    def __init__(self, conn):
        self.conn = conn

    def __iter__(self):
        # with conn.cursor(cursor_factory=DictCursor) as cur:
            # TODO: save names of table and database
            # to a central location. For now, db=arxive and table=articles
        cur.execute("SELECT * FROM articles;")
        for patent in conn['patents'].find():
            abstract = patent['_source']['patent-document']['abstract']['p']['text'].replace('\n', ' ').strip()
            # train on body, composed of title and abstract
            # body = patent['title'] + '. '
            body += abstract
            # We want to keep some punctuation, as Word2Vec
            # considers them useful context
            words = re.findall(r"[\w']+|[.,!?;]", body)
            # lowercase. perhaps lemmatize too?
            words = [word.lower() for word in words]
            # document tag. Unique integer 'index' is good.
            # can also add topic tag of form
            # 'topic_{subject_id}' to list
            #tags = [patent['index'], patent['subject']]
            tags = [patent['index']]

            yield TaggedDocument(words, tags)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='trains model based on corpus in psql')
    parser.add_argument('dbname', help="Name of postgres database")
    parser.add_argument('path_to_model', help="Filepath and name for model")
    args = parser.parse_args()

    n_cpus = multiprocessing.cpu_count()
    db = MongoClient()[args.dbname]
    doc_iterator = DocIterator(db)
    model = Doc2Vec(documents=doc_iterator, workers=n_cpus, size=100)

    model.save(args.path_to_model)
    print("Model can be found at %s"%args.path_to_model)
