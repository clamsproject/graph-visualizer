from mmif import Mmif, View, AnnotationTypes, DocumentTypes
from tqdm import tqdm
import json
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
import argparse 


tqdm.pandas()

MAX_LEN = 1024 # Summarizer needs at least 4GB 

device = torch.device("cuda:0" if torch.cuda.is_available() and torch.cuda.mem_get_info()[1] > 4000000000 else "cpu")
print(f"Using device: {device}")

# Transformer-based Summarizer 
def load_transformer():
    from transformers import pipeline
    return pipeline("summarization", model="facebook/bart-large-cnn", device=device)

def generate_abstractive_summary(asr_text: str, summarizer, max_len=150):
    min_len = 30 if max_len > 30 else int(max_len/2)
    return summarizer(asr_text, max_length=max_len, min_length=min_len, do_sample=False)[0]['summary_text']

def summarize_transformer(asr_text: str):
    summarizer = load_transformer()
    if len(asr_text) > MAX_LEN:
        chunks = [asr_text[i:i+MAX_LEN] for i in range(0, len(asr_text), MAX_LEN)]
        summaries = [generate_abstractive_summary(chunk, summarizer, max_len=int(math.floor(MAX_LEN/len(chunks)))) for chunk in tqdm(chunks)]
        asr_text = " ".join(summaries)
    return generate_abstractive_summary(asr_text, summarizer), asr_text

#  LLM Summarizer 
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
            text = annotation.properties.get("text")
            return text if isinstance(text, str) else text.value



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





def summarize_file(mmif: Mmif, method: str):
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
    
    if method == "llm":
        summary, long_summary = summarize_from_text(asr_text)
        return summary, long_summary, asr_text
    elif method == "transformer":
        summary, long_summary = summarize_transformer(asr_text)
        return summary, long_summary, asr_text
    else:
        raise ValueError("Invalid summarization method")


def process_dataset_for_examples():
    """
    Instead of traditional fine-tuning, prepare examples for few-shot learning
    """
    try:
        df = pd.read_csv("../data/descriptions.csv")
        print("Processing dataset to create few-shot examples")
        
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


def is_mmif(content):
    try:
        obj = json.loads(content)
        return "@type" in obj and "MMIF" in obj["@type"]
    except json.JSONDecodeError:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize MMIF transcript using --llm or --transformer.")
    parser.add_argument("--llm", action="store_true", help="Use LLM (Gemma3) summarizer")
    parser.add_argument("--transformer", action="store_true", help="Use Transformer (BART) summarizer")
    parser.add_argument("input_file", type=str, help="Path to MMIF JSON file")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)

    if args.llm:
        method = "llm"
    elif args.transformer:
        method = "transformer"
    else:
        print("You must specify either --llm or --transformer")
        sys.exit(1)

    with open(args.input_file, "r") as f:
        content = f.read()

    print("Generating summary...")
    
    if is_mmif(content):
        mmif = Mmif(content)
        summary, long_summary, asr_text = summarize_file(mmif, method)
    else:
       
        if method == "llm":
            summary, long_summary = summarize_from_text(content)
        elif method == "transformer":
            summary, long_summary = summarize_transformer(content)
        else:
            raise ValueError("Invalid summarization method")
        asr_text = content  

    print("\nSummary:\n", summary)