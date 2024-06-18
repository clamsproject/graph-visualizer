from bertopic import BERTopic
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
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

from .ner import get_entities

# If you have less than 4GB of VRAM, your computer will have a bad time running BERTopic
device = torch.device("cuda:0" if torch.cuda.is_available() and torch.cuda.mem_get_info()[1] > 4000000000 
                               else "cpu")

try:
    topic_model = BERTopic.load(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/base_topic")))
    print("Loaded pretrained topic model.")
except Exception as e:
    print("WARNING: failed to load pre-trained topic model. Topic modeling will not work in the visualization.")


def preprocess(text, entities):
    """
    Preprocess text for topic modelling by removing named entities and stop words
    """
    entities = [entity.lower() for entity in entities]
    # Split multi-word entities
    entities = [entity for expression in entities for entity in expression.split()]
    return " ".join([word for word in word_tokenize(text) \
                     if word.lower() not in entities \
                     and word.lower() not in stopwords.words("english")])


def get_topics(docs, entities=[], zeroshot_topics=[]):
    print("Getting topics...")
    # Flatten list and split into sliding window n-grams.
    # This is so the topic model has more information to train on. This works
    # in this case, since the long summaries generally contain many different
    # topics that vary from sentence to sentence.
    flattened_docs = "".join([doc for sublist in docs for doc in sublist])
    flattened_docs = preprocess(flattened_docs, entities)
    sentences = sent_tokenize(flattened_docs)
    three_sent_ngrams = [" ".join(sentences[i:i+3]) for i in range(len(sentences)-2)]
    print(f"Training on {len(three_sent_ngrams)} n-grams.")
    # We want the zero-shot topics to show up in the graph view, even if very few
    # documents are classified under those topics. To avoid having to lower the
    # zeroshot_min_similarity threshold too much while still keeping zeroshot
    # topics, we add temp "dummy" documents guranteed to be classified under the
    # zeroshot topics during training (in practice this seems to work very well).
    if zeroshot_topics:
        three_sent_ngrams += [(topic + " ") * 10 for topic in zeroshot_topics]

    has_zeroshot = len(zeroshot_topics) > 0
    topic_model, _ = train_topic_model(docs=three_sent_ngrams, zeroshot_topics=zeroshot_topics)
    probs, _ = topic_model.approximate_distribution(docs, use_embedding_model=has_zeroshot)

    # Normalize for better visualization
    print("Normalizing...")
    probs = (probs - probs.min(axis=0)) / (probs.max(axis=0) - probs.min(axis=0))
    print("Removing NaNs...")
    probs[probs != probs] = 0
    topic_info = topic_model.get_topic_info()
    topic_names = {topic: name for topic, name in zip(topic_info["Topic"], topic_info["Name"])}
    return topic_names, probs.tolist()


def train_topic_model(docs, zeroshot_topics = []):
    """
    Train zero-shot topic model. If no zero-shot topics are specified, this is a standard topic model.
    """
    # max_df to filter out extremely common words, and min_df to filter out rare but influential words
    # like names
    # vectorizer_model = TfidfVectorizer(stop_words='english')
    vectorizer_model = TfidfVectorizer(max_df=0.99, min_df=0.6, stop_words='english')
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    representation_model = MaximalMarginalRelevance(diversity=0.015)

    hdbscan_model = HDBSCAN(min_cluster_size=10, metric='euclidean', 
                        cluster_selection_method='eom', prediction_data=True, min_samples=5)

    # Enable low_memory if you run out of memory
    topic_model = BERTopic(
        # vectorizer_model=vectorizer_model,
        # ctfidf_model=ctfidf_model,
        # hdbscan_model=hdbscan_model,
        zeroshot_topic_list=zeroshot_topics if zeroshot_topics else None,
        zeroshot_min_similarity=.65 if zeroshot_topics else None,
        # low_memory=True
    )

    print("Training topic model...")
    topic_model.fit(docs)

    print("Trained topic model.")

    print(topic_model.get_topic_info()["Name"])

    return topic_model, docs


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
    data["transcript"] = data["transcript"].progress_apply(preprocess)

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
    # from eval.topic import get_coherence

    # # best_model, data = grid_search_topic_model()
    # # print(best_model.get_topic_info()["Name"])

    # data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/transcripts.csv"))
    # data = data.dropna()

    # topic_model, data = train_topic_model()
    # coherence = get_coherence(topic_model, data['transcript'][:1000] if len(data) > 1000 else data['transcript'])
    # print(topic_model.get_topic_info()["Name"])

    # print(f"Topic Model Coherence: {coherence}")

    from datasets import load_dataset

    dataset = load_dataset("CShorten/ML-ArXiv-Papers")["train"]
    docs = dataset["abstract"][:5_000]

    # We define a number of topics that we know are in the documents
    zeroshot_topic_list = ["Clustering", "Topic Modeling", "Large Language Models"]

    topic_model = BERTopic(
        embedding_model="thenlper/gte-small", 
        min_topic_size=15,
        zeroshot_topic_list=zeroshot_topic_list,
        zeroshot_min_similarity=.85,
        representation_model=KeyBERTInspired()
    )
    topic_model.fit(docs)  
    probs, _ = topic_model.approximate_distribution(docs, use_embedding_model=True)  