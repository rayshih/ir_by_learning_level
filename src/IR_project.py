from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
import numpy as np

vectorizer = TfidfVectorizer(input='content',max_df=0.75,min_df=3)
kmeans = MiniBatchKMeans(n_clusters=5)	#reading levels = n_clusters

data = []
filename = 'items_Trunk_5.jl'
queryfile = 'xxx'
with open(filename) as fp:
	for line in fp:
		line.strip()
		data.append(line)
		
'''
load query as 'querydata'
'''
vectorizer.fit(data)
feature_data = vectorizer.fit(data)
feature_query = vectorizer.fit(querydata)

kmeans.fit(feature_data)
level_data = kmeans.predict(feature_data)
level_query = kmeans.predict(feature_query)

'''
decide each cluster to their corresponding reading level
adjust their label to correct reading level and split feature_data = feature_data_level[# of reading levels]
'''

for k in range(len(level_query)):	# process each query
	reading_level = level_query[k]
	document_ranking = np.zeros(len(feature_data_level[reading_level]))
	for i in ragne(len(feature_data_level[reading_level])):
		document_ranking[i] = np.dot(feature_data_level[reading_level][i],feature_query[k])	# basic dot similarity
	

	



