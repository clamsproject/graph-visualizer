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

topic_model = BERTopic.load(os.path.join(os.path.dirname(__file__), "../data/topic_newshour"))
print("Loaded pretrained topic model.")

def get_topics(docs):
    print("Getting topics...")
    topic_distr, _ = topic_model.approximate_distribution(docs, batch_size=100)
    # Normalize for better visualization
    topic_distr = (topic_distr - topic_distr.min(axis=0)) / (topic_distr.max(axis=0) - topic_distr.min(axis=0))
    # Remove NaNs
    topic_distr[topic_distr != topic_distr] = 0
    # print(topic_distr)
    # print("----------->")
    # topic_distr = softmax(topic_distr, axis=1)
    # print(topic_distr)
    topic_info = topic_model.get_topic_info()
    topic_names = {topic: name for topic, name in zip(topic_info["Topic"], topic_info["Name"])}
    return topic_names, topic_distr.tolist()

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


def train_topic_model():
    vectorizer_model = CountVectorizer(stop_words="english")
    # ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    # representation_model = MaximalMarginalRelevance(diversity=0.1)

    topic_model = BERTopic(vectorizer_model=vectorizer_model)
    tqdm.pandas()
    data = pd.read_csv("../data/transcripts.csv")
    data = data.dropna()
    # data['transcript'] = data['transcript'].progress_apply(preprocess_text)
    print("Training topic model...")
    topic_model.fit(data['transcript'])
    topic_model.save("../data/topic_newshour")
    print("Trained topic model.")
    print(topic_model.get_topic_info()["Name"])

if __name__ == "__main__":
    train_topic_model()