from bertopic import BERTopic
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from bertopic.representation import KeyBERTInspired
from hdbscan import HDBSCAN
import os
import json
from tqdm import tqdm
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired
from bertopic.representation import MaximalMarginalRelevance
from scipy.special import softmax
import torch

from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from sentence_transformers import SentenceTransformer

# If you have less than 4GB of VRAM, your computer will have a bad time running BERTopic
device = torch.device("cuda:0" if torch.cuda.is_available() and torch.cuda.mem_get_info()[1] > 4000000000 
                               else "cpu")

try:
    topic_model = BERTopic.load(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/base_topic")))
    print("Loaded pretrained topic model.")
except Exception as e:
    print("WARNING: failed to load pre-trained topic model. Topic modeling will not work in the visualization.")


def get_topics(docs):
    print("Getting topics...")
    probs, _ = topic_model.approximate_distribution(docs)

    # Normalize for better visualization
    print("Normalizing...")
    probs = (probs - probs.min(axis=0)) / (probs.max(axis=0) - probs.min(axis=0))
    print("Removing NaNs...")
    probs[probs != probs] = 0
    topic_info = topic_model.get_topic_info()
    topic_names = {topic: name for topic, name in zip(topic_info["Topic"], topic_info["Name"])}
    return topic_names, probs.tolist()

def remove_speaker_names(text):
    """
    Helper function to remove speaker names from text. (e.g. JIM LEHRER: ...)
    """
    speaker_split = text.split(":")
    if len(speaker_split) > 1 and len(speaker_split[0]) < 30:
        return ":".join(speaker_split[1:])
    return text

def train_topic_model(zeroshot_topics = []):
    """
    Train zero-shot topic model. If no zero-shot topics are specified, this is a standard topic model.
    """
    # max_df to filter out extremely common words, and min_df to filter out rare but influential words
    # like names
    vectorizer_model = TfidfVectorizer(max_df=0.99, min_df=0.6, stop_words='english')
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    representation_model = MaximalMarginalRelevance(diversity=0.015)

    # Enable low_memory if you run out of memory
    topic_model = BERTopic(
        vectorizer_model=vectorizer_model,
        zeroshot_topic_list=zeroshot_topics if zeroshot_topics else None,
        zeroshot_min_similarity=.5 if zeroshot_topics else None,
        # low_memory=True
    )

    tqdm.pandas()
    data = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/transcripts.csv")))
    data = data.dropna()
    print("removing speaker names...")
    data["transcript"] = data["transcript"].progress_apply(remove_speaker_names)

    print("Training topic model...")
    topic_model.fit(data['transcript'])
    topic_model.save(os.path.join(os.path.dirname(__file__), "../data/topic_newshour"))

    print("Trained topic model.")

    print(topic_model.get_topic_info()["Name"])

    return topic_model, data


def grid_search_topic_model(zeroshot_topics=[]):
    """
    Perform a grid search to optimize the topic model hyperparameters.
    Metric is the square of coherence and sparseness.
    """
    from sklearn.model_selection import ParameterGrid
    tqdm.pandas()
    data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/transcripts.csv"))
    data = data.dropna()
    print("removing speaker names...")
    data["transcript"] = data["transcript"].progress_apply(remove_speaker_names)

    # Define the parameter grid
    param_grid = {
        'vectorizer_model': [TfidfVectorizer(stop_words="english", max_df=0.98), CountVectorizer(stop_words="english", max_df=0.98), None],
        'ctfidf_model': [ClassTfidfTransformer(reduce_frequent_words=True), None],
        'representation_model': [MaximalMarginalRelevance(diversity=0.015), MaximalMarginalRelevance(diversity=0.02), KeyBERTInspired()],
        'n_gram_range': [(1, 1), (1, 2)],
        'min_topic_size': [10, 15, 20, 25],
    }

    # Generate all combinations of parameters
    param_combinations = list(ParameterGrid(param_grid))

    best_metric = -float('inf')
    best_topic_model = None

    for params in param_combinations:
        print(params)
        topic_model = BERTopic(**params)
        topic_model.fit(data['transcript'])
        coherence = get_coherence(topic_model, data['transcript'][:1000] if len(data) > 1000 else data['transcript'])
        sparseness = topic_model.approximate_distribution(data['transcript'])[0]
        sparseness = (sparseness == 0).sum()
        
        metric = (coherence*sparseness)
        print(metric)
        print("----------")
        if metric > best_metric:
            best_metric = metric
            best_topic_model = topic_model

    best_topic_model.save(os.path.join(os.path.dirname(__file__), "../data/best_topic_newshour"))
    return best_topic_model, data


if __name__ == "__main__":
    from eval.topic import get_coherence

    # best_model, data = grid_search_topic_model()
    # print(best_model.get_topic_info()["Name"])

    data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/transcripts.csv"))
    data = data.dropna()

    topic_model, data = train_topic_model()
    coherence = get_coherence(topic_model, data['transcript'][:1000] if len(data) > 1000 else data['transcript'])
    print(topic_model.get_topic_info()["Name"])

    print(f"Topic Model Coherence: {coherence}")