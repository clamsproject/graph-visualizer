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
    distances = kmeans.fit_transform(embeddings)
    print("Assigning clusters...")
    for i, node in tqdm(enumerate(nodes)):
        node['cluster'] = int(kmeans.labels_[i])
        node['centroid_distance'] = distances[i][node['cluster']].item()
        node['is_representative'] = False
    for cluster_num in range(n_clusters):
        cluster_nodes = [node for node in nodes if node['cluster'] == cluster_num]
        centroid_distances = np.array([node['centroid_distance'] for node in cluster_nodes])
        lowest_distances = centroid_distances.argsort()[:5]
        for i in lowest_distances:
            cluster_nodes[i]['is_representative'] = True
    return nodes