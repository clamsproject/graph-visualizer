import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Function to extract named entities
def get_entities(sentence):
    print("Getting entities")
    doc = nlp(sentence)
    entities = [ent for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE", "NORP", "PRODUCT", "FAC", "DATE"]]
    return entities