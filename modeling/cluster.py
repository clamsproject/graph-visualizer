from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
import pandas as pd
import ast
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

model = SentenceTransformer('all-mpnet-base-v2')

def cluster_nodes(nodes, n_clusters):
    summaries = [node['summary'] for node in nodes]
    embeddings = np.array(model.encode(summaries))
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(embeddings)
    for i, node in tqdm(enumerate(nodes)):
        node['cluster'] = int(kmeans.labels_[i])
    return nodes