import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
import os
import json
from tqdm import tqdm
import numpy as np
import requests
from collections import Counter
import math
from sklearn.metrics.pairwise import cosine_similarity
import re
from scipy.special import softmax
import torch



# If you have less than 4GB of VRAM, your computer will have a bad time running BERTopic
device = torch.device("cuda:0" if torch.cuda.is_available() and torch.cuda.mem_get_info()[1] > 4000000000 
                               else "cpu")
print(f"Using {device}")

# Constants
MAX_LEN = 1024 
# try:
#     topic_model = BERTopic.load(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/base_topic")))
#     print("Loaded pretrained topic model.")
# except Exception as e:
#     print("WARNING: failed to load pre-trained topic model. Topic modeling will not work in the visualization.")


def preprocess(text, entities):
    """
    Preprocess text for topic modelling by removing named entities and stop words
    """
    entities = [entity.lower() for entity in entities]
    # Split multi-word entities
    entities = [entity for expression in entities for entity in expression.split()]
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    
    # Filter out stop words and entities
    filtered_tokens = [word for word in tokens 
                      if word.lower() not in entities 
                      and word.lower() not in stop_words]
    
    return " ".join(filtered_tokens)

def generate_llm_topics(text, num_topics=5, max_words_per_topic=5):
    """Generate topics using Ollama's LLM"""
    if not text or len(text.strip()) == 0:
        print("Warning: Empty text provided to topic generator")
        return []
        
    prompt = f"""Extract {num_topics} distinct topics from the following text. 
For each topic, provide a short descriptive name (2-3 words max) and up to {max_words_per_topic} keywords.
Format your response as a valid JSON like this:
{{
  "topics": [
    {{"name": "topic1_name", "keywords": ["keyword1", "keyword2", "keyword3"]}},
    {{"name": "topic2_name", "keywords": ["keyword1", "keyword2", "keyword3"]}}
  ]
}}

Here is the text:
{text}
"""
    
    # Make API call to Ollama
    try:
        response = requests.post(OLLAMA_API_URL, 
                              json={
                                  'model': LLM_MODEL,
                                  'prompt': prompt,
                                  'stream': False,
                                  'options': {
                                      'temperature': 0.1
                                  }
                              }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # Try to parse JSON from the response
            json_str = result['response']
            
            # Extract JSON if it's wrapped in code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
            if json_match:
                json_str = json_match.group(1)
            
            # Find the JSON object within text
            json_pattern = r'({[\s\S]*})'
            json_match = re.search(json_pattern, json_str)
            if json_match:
                json_str = json_match.group(1)
            
            try:
                topics_data = json.loads(json_str)
                # Handle both direct topics or nested "topics" key
                if "topics" in topics_data:
                    return topics_data["topics"]
                else:
                    # If the model returned a list directly
                    if isinstance(topics_data, list):
                        return topics_data
                    # Handle unexpected structure
                    print("Warning: Unexpected JSON structure in LLM response")
                    return []
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON from LLM response: {e}")
                print(f"Raw response: {json_str}")
                return []
        else:
            print(f"Error calling Ollama API: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"Error processing LLM response: {e}")
        return []


def chunk_text(text, max_len=MAX_LEN):
    """Split text into manageable chunks for LLM processing"""
    if not text:
        return []
        
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length <= max_len:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def process_documents_for_topics(docs, num_topics=10, entities=None):
    """Process all documents to extract topics"""
    entities = entities or []
    print("Processing documents for topic modeling...")
    
    if not docs or all(not doc for doc in docs):
        print("Warning: No document content to process")
        return {}, []
    
    # Flatten list and preprocess
    flattened_docs = " ".join([doc for sublist in docs for doc in sublist if doc])
    flattened_docs = preprocess(flattened_docs, entities)
    
    # Split into manageable chunks
    chunks = chunk_text(flattened_docs)
    print(f"Processing {len(chunks)} text chunks")
    
    # Extract topics from each chunk
    all_topics = []
    for chunk in tqdm(chunks):
        chunk_topics = generate_llm_topics(chunk, num_topics=min(5, num_topics))
        all_topics.extend(chunk_topics)
    
    # Merge similar topics
    merged_topics = merge_similar_topics(all_topics, threshold=0.7)
    
    # Select top topics by frequency
    top_topics = select_top_topics(merged_topics, num_topics)
    
    # Create topic dictionary with IDs
    topic_names = {i: topic["name"] for i, topic in enumerate(top_topics)}
    
    # Calculate document-topic distribution
    topic_distributions = calculate_topic_distributions(docs, top_topics)
    
    return topic_names, topic_distributions


def merge_similar_topics(topics, threshold=0.7):
    """Merge similar topics based on keyword overlap"""
    if not topics:
        return []
        
    merged = []
    
    for topic in topics:
        if not isinstance(topic, dict) or "keywords" not in topic or "name" not in topic:
            print(f"Warning: Invalid topic format: {topic}")
            continue
            
        name = topic["name"]
        keywords = set(topic["keywords"])
        
        # Check if this topic should be merged with an existing one
        merged_with_existing = False
        for existing in merged:
            existing_keywords = set(existing["keywords"])
            # Calculate Jaccard similarity
            overlap = len(keywords.intersection(existing_keywords))
            union_size = len(keywords.union(existing_keywords))
            
            if union_size > 0:  # Avoid division by zero
                similarity = overlap / union_size
                
                if similarity >= threshold:
                    # Merge keywords
                    existing["keywords"] = list(existing_keywords.union(keywords))
                    # Keep frequency count
                    existing["count"] = existing.get("count", 1) + 1
                    merged_with_existing = True
                    break
        
        if not merged_with_existing:
            topic["count"] = 1
            merged.append(topic)
    
    return merged


def select_top_topics(topics, num_topics):
    """Select top topics based on frequency"""
    if not topics:
        return []
        
    # Sort by count
    sorted_topics = sorted(topics, key=lambda x: x.get("count", 0), reverse=True)
    return sorted_topics[:num_topics]


def calculate_topic_distributions(docs, topics):
    """Calculate document-topic distribution using keyword presence"""
    if not topics:
        return [[] for _ in docs]
        
    # Extract all keywords
    all_keywords = {}
    for i, topic in enumerate(topics):
        for keyword in topic.get("keywords", []):
            if keyword in all_keywords:
                all_keywords[keyword].append(i)
            else:
                all_keywords[keyword] = [i]
    
    # Calculate distribution for each document
    distributions = []
    
    for doc_list in docs:
        doc_text = " ".join([d for d in doc_list if d]).lower()
        topic_counts = [0] * len(topics)
        
        # Count keyword occurrences
        for keyword, topic_ids in all_keywords.items():
            count = doc_text.count(keyword.lower())
            if count > 0:
                for topic_id in topic_ids:
                    topic_counts[topic_id] += count
        
        # Normalize to create a probability distribution
        total = sum(topic_counts)
        if total > 0:
            distribution = [count/total for count in topic_counts]
        else:
            distribution = [1.0/len(topics)] * len(topics)  # Uniform if no matches
        
        distributions.append(distribution)
    
    return distributions

def calculate_zeroshot_topic_distributions(docs, topics):
    """Calculate topic distribution using zero-shot classification with LLM"""
    if not topics:
        return [[] for _ in docs]
        
    distributions = []
    
    for doc_list in tqdm(docs, desc="Calculating zero-shot distributions"):
        doc_text = " ".join([d for d in doc_list if d])
        
        if len(doc_text) > MAX_LEN:
            doc_text = doc_text[:MAX_LEN]
        

        distribution = generate_llm_topic_distribution(doc_text, topics)
        distributions.append(distribution)
    
    return distributions
