import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from newspaper import Article

def get_main_article_text(row):
    url = row["SOURCEURL"]
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return None

def process_row(row):
    if int(row.name) % 100 == 0:
        print(f"Processing row {row.name}")
    article_text = get_main_article_text(row)
    if article_text:
        return {"entry": row.name, "ARTICLETEXT": article_text}
    else:
        return None

def scrape_in_parallel(df):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_row, row) for _, row in df.iterrows()]
        results = [future.result() for future in futures if future.result() is not None]
    return pd.DataFrame.from_records(results)

dataset_path = "bq-results.csv"
output_path = "bq-results-scraped.csv"

df = pd.read_csv(dataset_path)
df["entry"] = df.index

# Parallelize the processing of rows
scraped_df = scrape_in_parallel(df)

merged_df = pd.merge(df, scraped_df, on="entry", how="right")

# Drop rows with None values
scraped_df = scraped_df.dropna(subset=["ARTICLETEXT"])

# Save the results
merged_df.to_csv(output_path, index=False)