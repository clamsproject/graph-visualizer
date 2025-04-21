from mmif import Mmif, View, AnnotationTypes, DocumentTypes
from tqdm import tqdm
import torch
import math
import pandas as pd
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from nltk.tokenize import sent_tokenize
import numpy as np
import networkx as nx
from torch.utils.data import Dataset
import requests
import json
import sys
import os


tqdm.pandas()

MAX_LEN = 1024 # Summarizer needs at least 4GB 

if torch.cuda.is_available():
    try:
        free_memory = torch.cuda.mem_get_info()[1]
        device = torch.device("cuda:0" if free_memory > 4000000000 else "cpu")
    except:
        device = torch.device("cpu")
else:
    device = torch.device("cpu")

def generate_llm_summary(text, max_len=150):
    prompt = f"""Summarize the transcript in about {max_len} words.
    
{text}

Summary:"""

    response = requests.post('http://localhost:11434/api/generate', 
                           json={
                               'model': 'gemma3',
                               'prompt': prompt,
                               'stream': False,
                               'options': {
                                   'temperature': 0.1,  
                                   'top_p': 0.9
                               }
                           })
    
    if response.status_code == 200:
        result = response.json()
        return result['response'].strip()
    else:
        print(f"Error calling Ollama API: {response.status_code}")
        return "Error generating summary."



def url2posix(path):
    if path.startswith('file:///'):
        path = path[7:]
    return path

def get_transcript(mmif: Mmif):
    for document in mmif.documents:
        if document.at_type.shortname == "TextDocument":
            with open(url2posix(document.properties.location), "r") as f:
                return f.read()
    return None


def get_asr_views(mmif: Mmif):
    asr_views = []
    for view in mmif.views:
        if "whisper" in view.metadata.app and "warnings" not in view.metadata:
            asr_views.append(view)
    return asr_views


def get_asr_text(asr_view: View):
    for annotation in asr_view.annotations:
        if annotation.at_type.shortname == "TextDocument":
            return annotation.properties.get("text").value


def summarize_from_text(asr_text: str):
    if len(asr_text) > MAX_LEN:
        chunks = [asr_text[i:i+MAX_LEN] for i in range(0, len(asr_text), MAX_LEN)]
        chunk_summaries = []
        
        for chunk in tqdm(chunks):
            chunk_summary = generate_llm_summary(chunk, max_len=int(math.floor(150/len(chunks))))
            chunk_summaries.append(chunk_summary)
            
        if len(chunk_summaries) > 1:
            combined_summaries = " ".join(chunk_summaries)
            final_summary = generate_llm_summary(combined_summaries, max_len=150)
            return final_summary, combined_summaries
        else:
            return chunk_summaries[0], asr_text
    else:
        summary = generate_llm_summary(asr_text, max_len=150)
        return summary, asr_text





def summarize_file(mmif: Mmif):
    gold_transcript = get_transcript(mmif)
    if gold_transcript:
        asr_text = gold_transcript
    else:
        asr_views = get_asr_views(mmif)
        if not asr_views:
            return "No ASR views found in the MMIF file", "", ""
        asr_text = get_asr_text(asr_views[0])
        if not asr_text:
            return "No text found in ASR view", "", ""
    summary, long_summary = summarize_from_text(asr_text)
    return summary, long_summary, asr_text



def process_dataset_for_examples():
    """
    Instead of traditional fine-tuning, prepare examples for few-shot learning
    """
    try:
        df = pd.read_csv("../data/descriptions.csv")
        print("Processing dataset to create few-shot examples")
        
        # Select a subset of good examples
        sample_df = df.sample(n=5)
        examples = []
        
        for _, row in sample_df.iterrows():
            example = {
                "transcript": row["transcript"],
                "summary": row["description"]
            }
            examples.append(example)
        
        # Save examples for later use with the LLM
        with open("../data/few_shot_examples.json", "w") as f:
            json.dump(examples, f)
        
        print(f"Saved {len(examples)} examples for few-shot learning")
        return examples
    except Exception as e:
        print(f"Error processing dataset: {e}")
        return []


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        
        print(f"Reading transcript from '{input_file}'...")
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                transcript = f.read()
        except Exception as e:
            print(f"Error reading input file: {e}")
            sys.exit(1)
        
       
        print("Generating summary...")
        try:
            summary, full_text = summarize_from_text(transcript)
            print("\nSummary:")
            print(summary)
        except Exception as e:
            print(f"Error generating summary: {e}")
            sys.exit(1)
    