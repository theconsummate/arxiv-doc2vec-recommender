import multiprocessing
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import re
import sys
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
        for patent in self.conn['patents'].find():
            abstract = patent['_source']['patent-document']['abstract']['p']['text'].replace('\n', ' ').strip()
            # train on body, composed of title and abstract
            # body = patent['title'] + '. '
            # We want to keep some punctuation, as Word2Vec
            # considers them useful context
            words = re.findall(r"[\w']+|[.,!?;]", abstract)
            # lowercase. perhaps lemmatize too?
            words = [word.lower() for word in words]
            # document tag. Unique integer 'index' is good.
            # can also add topic tag of form
            # 'topic_{subject_id}' to list
            #tags = [patent['index'], patent['subject']]
            tags = [patent['_id']]

            yield TaggedDocument(words, tags)



if __name__ == '__main__':
    n_cpus = multiprocessing.cpu_count()
    db = MongoClient()[sys.argv[1]]
    doc_iterator = DocIterator(db)
    model = Doc2Vec(documents=doc_iterator, workers=n_cpus, size=100)
    path = './doc2vec_model'
    model.save(path)
    print("Model can be found at " + path)
