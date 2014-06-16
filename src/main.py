import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans

def readFile(filename):
  data = []

  with open(filename) as fp:
    for line in fp:
      line.strip()
      data.append(line)

  return data

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
  kmeans.fit(feature_data)

  return kmeans, vectorizer

def index(filename):
  data = readFile(filename)

  # TODO create a jl file reader

  kmeans, vectorizer = train(data)

  # TODO save the indexing result

def main():
  action = sys.argv[1]

  if action == 'index':
    index(sys.argv[2])
  else:
    print "action %s not supported" % (action)


if __name__ == "__main__":
  main()
