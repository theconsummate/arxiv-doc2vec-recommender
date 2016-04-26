
# coding: utf-8

# In[1]:

import sys
import os
import json
import requests
import time
from pymongo import MongoClient
import pymongo.errors as pyerror
# init the database object
db = MongoClient()['patent']


cpc_file = open('cpc.txt', 'r')
for cpc in cpc_file.readlines():
    #cpc classification tag
    # cpc = "A01B"


    #how many patents get returned in the results list
    RESULT_SIZE = 100000

    #output: what fiels in the json are returned as part of the results
    REQUIRED_FIELDS = [ 'patent-document.@ucid' ]


    base_url = "https://search-bouncypepper-m4utjzuqkoj5ahb32jfqokwvz4.us-west-2.es.amazonaws.com"
    index_name = "/ifi"
    type_name = "/publication"
    pretty = "?pretty=true"

    url = base_url + index_name + type_name + "/_search" + pretty

    query = {
    		"_source" : {
    			"include" : REQUIRED_FIELDS
    		},
    	"from" : 0, "size" : RESULT_SIZE,
        "query" : {
            "filtered" : {
                "query" : {
                    "bool" : {
                        "must" : [
                            {
                                "match" : {
                                "patent-document.bibliographic-data.technical-data.classifications-cpc.classification-cpc.$t" : {
                                        "query" : cpc
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }



    startTime2 = time.time()
    data = json.dumps(query)
    #print ('json dump time: ' + str(time.time() - startTime2))
    startTime6 = time.time()
    req = requests.get(url, data = data)
    # req = requests.get(url)
    #print ('get from ES time: ' + str(time.time() - startTime6))
    response = req.content

    # print response

    json_data = json.loads(response)

    with open('results.txt', 'w') as outfile:
        json.dump(json_data, outfile)
        outfile.close()


    # In[17]:

    with open('results.txt', 'r') as results:
        data = json.load(results)
        results.close()

    patent_results_list = []

    for x in data["hits"]["hits"]:
        val = x["_source"]["patent-document"]["@ucid"]
        patent_results_list.append(val)

    REQUIRED_FIELDS = [
                    'patent-document.abstract.p.$t',
                  ]

    for x in patent_results_list:

        query = {
                "_source" : {
                    "include" : REQUIRED_FIELDS
                },
            "from" : 0, "size" : 1,
            "query" : {
                "filtered" : {
                    "query" : {
                        "bool" : {
                            "must" : [
                                {
                                    "match" : {
                                        "patent-document.@ucid": {
                                            "query" : x,
                                            }
                                      }
                                }
                            ]
                        }
                    }
                }
            }
        }

        data = json.dumps(query)
        req = requests.get(url, data = data)
        response = req.content

        json_data = json.loads(response)

        filename = x + '.txt'
        try:
            for data in json_data['hits']['hits']:
                print "Inserting : " + x
                if 'patent-document' not in data['_source'].keys():
                    print 'source is empty'
                    break
                if isinstance(data['_source']['patent-document']['abstract']['p'], list):
                    full_text = ''
                    for text_item in data['_source']['patent-document']['abstract']['p']:
                        full_text += text_item['$t']
                    data['_source']['patent-document']['abstract']['p'] = {'text': full_text}
                else:
                    data['_source']['patent-document']['abstract']['p']['text'] = data['_source']['patent-document']['abstract']['p'].pop('$t')
                data['_cpc'] = cpc
                db['patents'].insert_one(data)
        except pyerror.DuplicateKeyError:
            print "trying to insert duplicate: " + x

cpc_file.close()
    # with open(filename, 'w') as outfile:
    #     #json_data needs to be cleaned before outputting to file
    #     json.dump(json_data, outfile)
    #     outfile.close()




# In[ ]:




# In[ ]:



