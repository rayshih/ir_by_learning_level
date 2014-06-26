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
import operator
#from gensim import corpora, models, matutils

# '''
# decide each cluster to their corresponding reading level
# adjust their label to correct reading level and split feature_data = feature_data_level[# of reading levels]
# '''
#
# for k in range(len(level_query)):	# process each query
# 	reading_level = level_query[k]
# 	document_ranking = np.zeros(len(feature_data_level[reading_level]))
# 	for i in ragne(len(feature_data_level[reading_level])):
# 		document_ranking[i] = np.dot(feature_data_level[reading_level][i],feature_query[k])	# basic dot similarity

def replace(string):
    string = string.replace('<',' ')
    string = string.replace('>',' ')
    string = string.replace('-',' ')
    string = string.replace('_',' ')
    string = string.replace('/',' ')
    string = string.replace(',',' ')
    string = string.replace('=',' ')
    string = string.replace('\\',' ')
    return string 

def train(data):

  vectorizer = TfidfVectorizer(input='content',max_df=0.75,min_df=3)
  #lsa = TruncatedSVD(n_components=20000,algorithm='randomized',n_iterations=5)
  # preprocessing
  for i in range(len(data)):
      data[i] = replace(data[i])
  feature_data = vectorizer.fit_transform(data)
  print 'feature_shape',feature_data.shape
  
  #dictionary = corpora.Dictionary([vectorizer.get_feature_names()])
  #corpus = matutils.Sparse2Corpus(scipy.sparse.csr_matrix.transpose(feature_data))
  #lsi = models.LsiModel(corpus,id2word=dictionary, num_topics=10000)
  #feature_data = numpy.transpose(matutils.corpus2dense(lsi[corpus],10000))
  
  #print 'lsa_shape' ,feature_data.shape

  #feature_id = []
  #for i in xrange(len(feature_data)):
  #    feature_id.append(i)
  #indexed_data = [(idx, val) for idx, val in enumerate(feature_data)]
  return feature_data, vectorizer
  #return feature_data, vectorizer, lsi
  #return feature_data, vectorizer, lsa

  #kmeans = KMeans(n_clusters=3)	#reading levels = n_clusters
  # kmeans.fit(feature_data)

def index(filename):
  raw = reader.loadJL(filename)
  data = [util.get_searchable(item) for item in raw];
  print 'index finish'
  #indexed_data, vectorizer, lsa = train(data)
  indexed_data, vectorizer = train(data)
  print 'vectorizer finish'

  Persist("indexed_data").dump(indexed_data)
  Persist("vectorizer").dump(vectorizer)
  #Persist('lsa').dump(lsa)
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
  #print indexed_data.shape
  #exit(0)

  vectorizer = Persist("vectorizer").load()
  queryVector = vectorizer.transform([queryString])[0]
  '''
  queryVector = matutils.Sparse2Corpus(scipy.sparse.csr_matrix.transpose(queryVector))

  lsi = Persist('lsa').load()
  #queryVector = lsi[queryVector]
  queryVector = numpy.transpose(matutils.corpus2dense(lsi[queryVector],10000))
  '''

  #queryVector = lsa.transform(vectorizer.transform([queryString])[0])
  #dictionary = vectorizer.get_feature_names()
  #for item in dictionary:
  #    print item.encode('utf-8')
  #exit(1)
  
  #queryVector = vectorizer.transform([queryString])[0]

  #print 'query shape',queryVector.shape
  #print 'data shape',indexed_data.shape
  #exit(1)
  
  #scores = []
  #scores = queryVector.dot(indexed_data.T)
  scores = indexed_data.dot(queryVector.T)
  
  index = []
  relevant_data = []
  for e,s in enumerate(scores):
    if s > 0:
      index.append(e)
      #relevant_data.append(indexed_data[e].todense())
      #print s
  print 'score done'
  #data = np.asarray(relevant_data)
  data = indexed_data[index].todense()
  #print data.shape
  #print data[0].shape
  #exit(1)
  #result = sorted(scores, key=lambda x:-x[1])
  
  #index = [item[0] for item in result if item[1] > 0.001]
  seed = ['easy','medium','hard']
  #seed = lsa.transform(vectorizer.transform(seed))
  
  seed = vectorizer.transform(seed)
  seed = seed.todense()

  #print 'seed shape',seed.shape
  #print 'data shape',data.shape
  
  #print data.dtype, seed.dtype
  
  kmeans = KMeans(n_clusters=3,init=seed)

  kmeans.fit(data)
  label = kmeans.predict(data)
  print 'KMeans done'
  #print label
  #indexed_subdata = [[],[],[]]
  subdata = []
  sub_origin_index = [[],[],[]]
  sub_query_index = [[],[],[]]

  for i in xrange(len(data)):
    #indexed_subdata[label[i]].append((index[i],data[i]))
    #subdata[label[i]].append(data[i])
    sub_query_index[label[i]].append(i)
    sub_origin_index[label[i]].append(index[i])
  
  for i in xrange(3):
    #sub = np.asarray(data[sub_query_index].todense())
    subdata.append(data[sub_query_index[i]])
    #print 'sub',i,'shape',subdata[i].shape
    print 'tutorial level',i+1
    for j in xrange(3):
      print 'document',sub_origin_index[i][j]
  exit(1)
  scores = [[],[],[]]


  for i in xrange(3):
    #scores[i] = [(item[0], item[1].dot(queryVector.T)[0,0]) for item in indexed_subdata]
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
