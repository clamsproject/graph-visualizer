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
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired
from bertopic.representation import MaximalMarginalRelevance
from scipy.special import softmax
import torch

from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from sentence_transformers import SentenceTransformer

# topics = [
#     'Political Scandals',
#     'Military Conflicts',
#     'International Tensions',
#     'Energy and Natural Resources',
#     'Hostage Crises',
#     'Economic Policies',
#     'Geopolitical Shifts',
#     'Wars and Military Operations',
#     'Presidential Controversies',
#     'Regional Conflicts',
#     'Economic Bubbles and Crashes',
#     'Terrorism',
#     'Foreign Wars',
#     'Weapons of Mass Destruction',
#     'Natural Disasters',
#     'Financial Crises',
#     'Historic Elections',
#     'Healthcare Issues',
#     'Protests and Uprisings',
#     'Civil Wars',
#     'National Security Leaks',
#     'Disease Outbreaks',
#     'Environmental Issues',
#     'Supreme Court Decisions',
#     'Electoral Politics'
# ]    


# nltk.download('punkt')
# nltk.download('stopwords')
# hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
# topic_model = BERTopic(
#     embedding_model="thenlper/gte-small", 
#     min_topic_size=15,
#     zeroshot_topic_list=topics,
#     zeroshot_min_similarity=.85,
#     representation_model=KeyBERTInspired(),
#     hdbscan_model=hdbscan_model
# )


device = torch.device("cpu")

topic_model = BERTopic.load(os.path.join(os.path.dirname(__file__), "../data/topic_newshour"))
print("Loaded pretrained topic model.")

def get_topics(docs):
    print("Getting topics...")
    preds, probs = topic_model.transform(docs)
    # topic_distr, _ = topic_model.approximate_distribution(docs, batch_size=50, use_embedding_model=True)
    # Normalize for better visualization
    print("Normalizing...")
    probs = (probs - probs.min(axis=0)) / (probs.max(axis=0) - probs.min(axis=0))
    # Remove NaNs
    print("Removing NaNs...")
    probs[probs != probs] = 0
    # print(topic_distr)
    # print("----------->")
    # topic_distr = softmax(topic_distr, axis=1)
    # print(topic_distr)
    topic_info = topic_model.get_topic_info()
    topic_names = {topic: name for topic, name in zip(topic_info["Topic"], topic_info["Name"])}
    return topic_names, probs.tolist()

def remove_stop_words(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    return " ".join(filtered_sentence)

def preprocess_text(text):
    print("Preprocessing...")
    text = remove_stop_words(text)

def remove_speaker_names(text):
    speaker_split = text.split(":")
    if len(speaker_split) > 1 and len(speaker_split[0]) < 30:
        return ":".join(speaker_split[1:])
    return text

def train_topic_model(zeroshot_topics = []):
    # TODO: Get token-level contributions? (stretch goal)
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
    # embeddings = sentence_model.encode(docs, show_progress_bar=False)
    vectorizer_model = CountVectorizer(stop_words="english")
    # ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    # representation_model = MaximalMarginalRelevance(diversity=0.005)


    topic_model = BERTopic(
        vectorizer_model=vectorizer_model,
        # seed_topic_list=seed_topic_list
        min_topic_size=50,
        
        # ctfidf_model=ctfidf_model,
        zeroshot_topic_list=zeroshot_topics if zeroshot_topics else None,
        zeroshot_min_similarity=.5 if zeroshot_topics else None,
        calculate_probabilities=True,
        # representation_model=representation_model,
        embedding_model=sentence_model,
        # representation_model=KeyBERTInspired(),
        # low_memory=True
    )

    tqdm.pandas()
    data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/transcripts.csv"))
    data = data.dropna()
    print("removing speaker names...")
    data["transcript"] = data["transcript"].progress_apply(remove_speaker_names)
    # data['transcript'] = data['transcript'].progress_apply(preprocess_text)
    # data["transcript"] = data["transcript"].progress_apply(lambda x: x[:5000])
    print("Training topic model...")
    topic_model.fit(data['transcript'])
    # preds, probs = topic_model.transform(data['transcript'])
    # print(probs)
    # input()
    topic_model.save(os.path.join(os.path.dirname(__file__), "../data/topic_newshour"))
    print("Trained topic model.")

    # print("Getting distribution")
    # # topic_distr, _ = topic_model.approximate_distribution(data['transcript'], batch_size=500, use_embedding_model=True)
    # topic_distr, _ = topic_model.approximate_distribution(data['transcript'][:1000], batch_size=500)

    print(topic_model.get_topic_info()["Name"])

if __name__ == "__main__":
    train_topic_model()