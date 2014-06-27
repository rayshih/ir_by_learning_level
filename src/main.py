import sys
import string
import numpy as np
import scipy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
import data_reader as reader
import util
from persist import Persist
from pygraph.classes.digraph import digraph
from pygraph.algorithms import pagerank
from nltk.model import ngram
from urlparse import urlparse
import operator
import re

def replace(string):
    string = re.sub(r"<[^>]*>", " ", string)
    string = string.replace('-',' ')
    string = string.replace('_',' ')
    string = string.replace('/',' ')
    string = string.replace(',',' ')
    string = string.replace('=',' ')
    string = string.replace('\\',' ')
    return string

def train(data):

  vectorizer = TfidfVectorizer(input='content',max_df=0.75,min_df=3,ngram_range=(1,2))

  # preprocessing
  for i in range(len(data)):
      data[i] = replace(data[i])
  feature_data = vectorizer.fit_transform(data)
  print 'feature_shape',feature_data.shape
  return feature_data, vectorizer

def index(filename):
  raw = reader.loadJL(filename)
  raw = [item for item in raw if len(urlparse(item["url"]).path) > 2 ];
  data = [util.get_searchable(item) for item in raw];

  print 'index finish'
  indexed_data, vectorizer = train(data)
  print 'vectorizer finish'

  Persist("indexed_data").dump(indexed_data)
  Persist("vectorizer").dump(vectorizer)
  Persist("url_list").dump([item["url"] for item in raw])

def page_rank(filename):
    data = reader.loadJL(filename)
    gr = digraph()
    for site in data:
        if not gr.has_node(site["url"]):
            gr.add_nodes([site["url"]])
        for link in site["links"]:
            if not gr.has_node(link):
                gr.add_nodes([link])
            if not gr.has_edge((site["url"], link)):
                gr.add_edge((site["url"], link))

    pg_values = pagerank.pagerank(gr)
    Persist("page_rank").dump(pg_values)

    print 'page rank finish'

def search(queryString):
  indexed_data = Persist("indexed_data").load()
  urls = Persist('url_list').load()
  pg_values = Persist('page_rank').load()

  vectorizer = Persist("vectorizer").load()
  queryVector = vectorizer.transform([queryString])[0]
  scores = indexed_data.dot(queryVector.T)

  index = []
  relevant_data = []
  page_rank = []
  for e,s in enumerate(scores):
    if s > 0.03:
      index.append(e)
      page_rank.append(pg_values[urls[e]])
  print 'score done'
  data = indexed_data[index].todense()
  print 'relavent document size',data.shape

  label_raw = reader.loadJL('/tmp2/ir_labeled_data.jl')
  ldata = [util.get_searchable(item) for item in label_raw];
  label = [item['level'] for item in label_raw]
  seed = ['','','']
  for i in xrange(len(label)):
    ldata[i] = replace(ldata[i])
    if label[i] == 'Advanced':
      seed[2] += ldata[i]
    elif label[i] == 'Intermediate':
      seed[1] += ldata[i]
    elif label[i] == 'Beginner':
      seed[0] += ldata[i]
    else:
      print label[i],'Invalid......'
    if i %100==0:
      print label[i]

  seed = vectorizer.transform(seed)
  seed = seed.todense()

  kmeans = KMeans(n_clusters=3,init=seed)

  kmeans.fit(data)
  label = kmeans.predict(data)
  print 'KMeans done'

  data = scipy.sparse.csr_matrix(data)
  subdata = []
  sub_origin_index = [[],[],[]]
  sub_query_index = [[],[],[]]

  level = [[],[],[]]

  for i in xrange(data.shape[0]):
    sub_query_index[label[i]].append(i)
    sub_origin_index[label[i]].append(index[i])

    ################################################################
    # use page rank
    ################################################################

    level[label[i]].append((index[i],page_rank[i]))

  for i in xrange(3):
    subdata = data[sub_query_index[i]]
    print 'relavent # of',i,':',len(sub_query_index[i])
    result = subdata.dot(queryVector.T)

    ##############################################################
    #for e,r in enumerate(result):
    #  level[i].append((sub_origin_index[i][e],r))
    ##############################################################

    level[i] = sorted(level[i],key=lambda x:-x[1])
    print 'tutorial level',i+1
    for j in xrange(min(10,len(level[i]))):
      print 'document',level[i][j][0],urls[level[i][j][0]],level[i][j][1]

  exit(1)
  scores = [[],[],[]]

  for i in xrange(3):
    scores[i] = 1
    scores[i] = sorted(scores, key=lambda x:-x[1])

  return scores

def query(queries):
  url_list = Persist("url_list").load()

  queryString = string.join(queries)
  print "Here is your query:"
  print queryString
  print ''

  # array of doc_id
  result = search(queryString)
  for i in xrange(3):
    #result = [item for item in result if item[1] > 0.001]
    for item in result[i][:10]:
      print url_list[item[0]]
      print item
      print ""

def main():
  action = sys.argv[1]

  if action == 'index':
    index(sys.argv[2])
  elif action == 'query':
    query(sys.argv[2:])
  elif action == 'page_rank':
    page_rank(sys.argv[2])
  else:
    print "action %s not supported" % (action)

if __name__ == "__main__":
  main()
