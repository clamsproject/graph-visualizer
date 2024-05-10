import os
# from sklearn.model_selection import train_test_split
import pandas as pd
from tqdm import tqdm
import json
import xml.etree.ElementTree as ET
import requests
import time

# from summarize import summarize_from_text

tqdm.pandas()

TRANSCRIPT_PATH = "/llc_data/clams/wgbh/newshour-transcripts"

def is_json(x):
    return x[0] == "{" or x[0] == "["

def read_file(filename):
    with open(filename, "r") as f:
        return " ".join(f.read().split())

def get_transcripts():
    filenames = [f for f in os.listdir(TRANSCRIPT_PATH) if os.path.isfile(os.path.join(TRANSCRIPT_PATH, f))]
    df = pd.DataFrame(filenames, columns=["filename"])
    df["transcript"] = [read_file(os.path.join(TRANSCRIPT_PATH, file)) for file in df["filename"]]
    df = df[df["transcript"].progress_apply(lambda x: not is_json(x))]
    df.to_csv("../data/transcripts.csv")

def get_description_from_filename(filename):
    # To avoid rate limits
    time.sleep(1)
    guid = filename.split(".")[0]
    url = f"https://americanarchive.org/api/{guid}.xml"
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        descriptions = root.findall("{http://www.pbcore.org/PBCore/PBCoreNamespace.html}pbcoreDescription")
        # Results tend to include multiple descriptions. Get the longest one that has useful information.
        longest_description = max([" ".join(d.text.split()) for d in descriptions], key=len)
        if longest_description and "No other information" not in longest_description \
                               and "No information" not in longest_description \
                               and "No description" not in longest_description:
            return longest_description
    return None

def get_descriptions():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = pd.read_csv(os.path.join(parent_dir, "data/transcripts.csv"))
    df["description"] = df["filename"].progress_apply(lambda x: get_description_from_filename(x))
    df = df.dropna()

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df.to_csv(os.path.join(parent_dir, "data/descriptions.csv"))
    print(f"Finished getting descriptions. Dataset now contains {len(df)} instances.")

if __name__ == "__main__":
    get_transcripts()
    get_descriptions()