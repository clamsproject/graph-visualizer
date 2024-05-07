from mmif import Mmif
import re
import requests
import xml.etree.ElementTree as ET
import random
import time
from datetime import datetime
import ffmpeg
import os


def match_guid(text):
    match = re.match(r"cpb-aacip-.+-\w+", text)
    if match:
        return match.group()
    return None

def get_date_from_guid(guid):
    url = f"https://americanarchive.org/api/{guid}.xml"
    print(f"checking {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        descriptions = root.findall("{http://www.pbcore.org/PBCore/PBCoreNamespace.html}pbcoreAssetDate")
        for description in descriptions:
            date = description.text
            if date:
                return date


def extract_date(filename, mmif):
    try:

        guid = match_guid(filename)
        if guid:
            date = get_date_from_guid(guid)
            if date: return date

        print("No GUID found. Checking other documents...")
        mmif = Mmif(mmif)
        documents = mmif.documents
        for document in documents:
            guid = match_guid(document.location)
            if guid:
                date = get_date_from_guid(guid)
                if date: return date

        return datetime.fromtimestamp(os.path.getctime(filename))
    except Exception as e:
        return None

if __name__ == "__main__":
    TEST_MMIF = "/home/elora/just_transcript/unnamed-test.mmif"
    with open(TEST_MMIF) as f:
        mmif = f.read()
    print(extract_date("/home/elora/just_transcript/unnamed-test.mmif", mmif))