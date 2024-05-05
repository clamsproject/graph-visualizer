import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def get_main_article_text(row):
    url = row["SOURCEURL"]
    try:
        response = requests.get(url, timeout=60)
    except requests.exceptions.Timeout:
        return None
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        article_text = soup.find("div", {"class": "article-body"}).get_text()
    except AttributeError:
        pass
    try:
        article_text = soup.find("article").get_text()
    except AttributeError:
        return None
    return article_text

def process_row(row):
    print("processing row!")
    article_text = get_main_article_text(row)
    if article_text:
        return {"index": row.name, "ARTICLETEXT": article_text}
    else:
        return None

def scrape_in_parallel(df):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_row, row) for _, row in df.iterrows()]
        results = [future.result() for future in futures]
    return pd.DataFrame(results)

dataset_path = "bq-results.csv"
output_path = "bq-results-scraped.csv"

df = pd.read_csv(dataset_path)

# Parallelize the processing of rows
scraped_df = scrape_in_parallel(df)

# Drop rows with None values
scraped_df = scraped_df.dropna(subset=["ARTICLETEXT"])

# Save the results
scraped_df.to_csv(output_path, index=False)