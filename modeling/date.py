from mmif import Mmif
import re
import requests
import xml.etree.ElementTree as ET
import random
import time
from datetime import datetime


with open("/home/hayden/clams/mmif_files/just_transcript/just_transcript/cpb-aacip-507-0g3gx4598v.trn.mmif", "r") as f:
    TEST_MMIF = Mmif(f.read())

def match_guid(text):
    match = re.match(r"cpb-aacip-.+-\w+", text)
    if match:
        return match.group()
    return None

def extract_date(filename, mmif):
    guid = match_guid(filename)
    if guid:
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
    print("No date found. Assigning random date...")
    d = random.randint(1, int(time.time()))
    return datetime.fromtimestamp(d).strftime('%Y-%m-%d')

if __name__ == "__main__":
    print(extract_date("cpb-aacip-507-0g3gx4598v.trn", TEST_MMIF))