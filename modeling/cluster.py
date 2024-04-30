from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
import pandas as pd
import ast
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

model = SentenceTransformer('all-mpnet-base-v2')

def cluster_nodes(nodes, n_clusters, embeddings=None):
    """
    Cluster nodes using KMeans

     Args:
     nodes: list of nodes
     n_clusters: number of clusters
     embeddings (optional): precomputed embeddings for input
    """
    if embeddings is None:
        print("Collecting summaries...")
        summaries = [node['summary'] for node in tqdm(nodes)]
        print("Encoding summaries...")
        embeddings = np.array(model.encode(summaries))
    print("Fitting KMeans...")
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(embeddings)
    print("Assigning clusters...")
    for i, node in tqdm(enumerate(nodes)):
        node['cluster'] = int(kmeans.labels_[i])
    return nodes