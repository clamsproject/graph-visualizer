from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
import ast
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm
from sklearn.metrics import silhouette_score

model = TfidfVectorizer(stop_words='english')

def cluster_nodes(nodes, embeddings=None):
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
        embeddings = model.fit_transform(summaries)
        print(embeddings.shape)
    print("Fitting KMeans...")
    kmeans_vals = []
    sillhouettes = []
    for i in range(2, 10):
        kmeans = KMeans(n_clusters=i)
        distances = kmeans.fit_transform(embeddings)
        kmeans_vals.append(kmeans)
        sillhouettes.append(silhouette_score(distances, kmeans.labels_))

    kmeans = kmeans_vals[sillhouettes.index(max(sillhouettes))]
    distances = kmeans.transform(embeddings)
    n_clusters = len(kmeans.cluster_centers_)
    
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
    return nodes, n_clusters