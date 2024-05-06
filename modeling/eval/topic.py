from gensim.models.coherencemodel import CoherenceModel
from gensim.test.utils import common_corpus, common_dictionary
from gensim.corpora import Dictionary

def get_coherence(topic_model, docs):
    topic_names = {k: [word for word, _ in v] for k, v in topic_model.get_topics().items()}
    topic_list = list(topic_names.values())
    dictionary = Dictionary(topic_list)
    corpus = [dictionary.doc2bow(text) for text in topic_list]
    cm = CoherenceModel(topics=topic_list, corpus=corpus, dictionary=dictionary, coherence='u_mass')
    coherence = cm.get_coherence()
    return coherence