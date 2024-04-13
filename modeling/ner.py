import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Function to extract named entities
def get_entities(sentence):
    print("Getting entities")
    doc = nlp(sentence)
    entities = [ent.text for ent in doc.ents]
    return entities