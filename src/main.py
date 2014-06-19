import sys
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans

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

def train(data):

  vectorizer = TfidfVectorizer(input='content',max_df=0.75,min_df=3)
  kmeans = MiniBatchKMeans(n_clusters=5)	#reading levels = n_clusters

  feature_data = vectorizer.fit_transform(data)
  indexed_data = [(idx, val) for idx, val in enumerate(feature_data)]

  return indexed_data, vectorizer

  # kmeans.fit(feature_data)

def index(filename):
  raw = reader.loadJL(filename)
  data = [util.get_searchable(item) for item in raw];

  indexed_data, vectorizer = train(data)

  Persist("indexed_data").dump(indexed_data)
  Persist("vectorizer").dump(vectorizer)
  Persist("url_list").dump([item["url"] for item in raw])

def search(queryString):
  indexed_data = Persist("indexed_data").load()
  vectorizer = Persist("vectorizer").load()

  queryVector = vectorizer.transform([queryString])[0]

  scores = [(item[0], item[1].dot(queryVector.T)[0,0]) for item in indexed_data]
  result = sorted(scores, key=lambda x:-x[1])
  return result

def query(queries):
  url_list = Persist("url_list").load()

  queryString = string.join(queries)
  print "Here is your query:"
  print queryString
  print ''

  # array of doc_id
  result = search(queryString)
  result = [item for item in result if item[1] > 0.001]

  for item in result[:10]:
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
