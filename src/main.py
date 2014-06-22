import sys
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
import data_reader as reader
import util
from persist import Persist

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
    string = string.replace('/',' ')
    string = string.replace(',',' ')
    string = string.replace('=',' ')
    string = string.replace('\\',' ')
    return string 

def train(data):

  vectorizer = TfidfVectorizer(input='content',max_df=0.75,min_df=3)
  lsa = TruncatedSVD(n_components=50000,algorithm='arpack')
  # preprocessing
  for i in range(len(data)):
      data[i] = replace(data[i])
  feature_data = vectorizer.fit_transform(data)
  print 'feature_shape',feature_data.shape
  lsa.fit(feature_data)
  feature_data = lsa.transform(feature_data)
  indexed_data = [(idx, val) for idx, val in enumerate(feature_data)]

  return indexed_data, vectorizer, lsa

  kmeans = KMeans(n_clusters=3)	#reading levels = n_clusters
  # kmeans.fit(feature_data)

def index(filename):
  raw = reader.loadJL(filename)
  data = [util.get_searchable(item) for item in raw];
  print 'index finish'
  indexed_data, vectorizer, lsa = train(data)
  print 'vectorizer finish'

  Persist("indexed_data").dump(indexed_data)
  Persist("vectorizer").dump(vectorizer)
  Persist('lsa').dump(lsa)
  Persist("url_list").dump([item["url"] for item in raw])

def search(queryString):
  indexed_data = Persist("indexed_data").load()
  vectorizer = Persist("vectorizer").load()
  lsa = Persist('lsa').load()
  queryVector = lsa.transform(vectorizer.transform([queryString])[0])

  scores = [(item[0], item[1].dot(queryVector.T)[0,0]) for item in indexed_data]
  result = sorted(scores, key=lambda x:-x[1])
  
  index = [item[0] for item in result if item[1] > 0.001]
  data = [indexed_data[i][1] for i in index]
  data = np.asarray(data)

  seed = ['easy','median','hard']
  seed = lsa.transform(vectorizer.transform(seed))
  kmeans = KMeans(n_clusters=3,init=seed)

  kmeans.fit(data)
  label = kmeans.predict(data)
  
  indexed_subdata = [[],[],[]]
  for i in range(len(data))
    indexed_subdata[label[i]].append((index[i],data[i]))
  scores = [[],[],[]]
  for i in xrange(3):
    scores[i] = [(item[0], item[1].dot(queryVector.T)[0,0]) for item in indexed_subdata]
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
  for i in xrange(3)
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
  else:
    print "action %s not supported" % (action)


if __name__ == "__main__":
  main()
