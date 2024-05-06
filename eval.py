import sys
# sys.path.append("..") # Adds higher directory to python modules path.
from app import get_all_nodes
from transformers import AutoModelWithLMHead, AutoTokenizer
import random
from modeling.summarize import summarize_from_text
import pandas as pd
from rouge_score import rouge_scorer
from tqdm import tqdm
tqdm.pandas()


def evaluate_visualizer(n_trials=10):
    """
    Method for evaluating the visualizer!
    """
    nodes = get_all_nodes()
    print(len(nodes))
    trial_nodes = random.sample(nodes, n_trials)
    trial_summaries = [node["long_summary"] for node in trial_nodes]

    tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-question-generation-ap")
    model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-question-generation-ap")

    for summary in trial_summaries:
        context = summary
        # Leave answer blank (the model will still come up with a question!)
        answer = ""

        input_text = "answer: %s  context: %s </s>" % (answer, context)
        features = tokenizer([input_text], return_tensors='pt')

        output = model.generate(input_ids=features['input_ids'], 
                    attention_mask=features['attention_mask'], max_length=256)

        print(tokenizer.decode(output[0]))

def evaluate_summarizer():
    df = pd.read_csv("data/descriptions.csv")
    df["id"] = df["filename"].apply(lambda x: x.replace(".mmif", "").replace(".json", ""))
    nodes = get_all_nodes()

    summaries = [(node["id"], node["summary"]) for node in nodes]
    summaries = pd.DataFrame(summaries, columns=["id", "summary"])
    summaries = summaries.merge(df, on="id").dropna()

    scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)

    scores = summaries.progress_apply(lambda x: scorer.score(x["description"], x["summary"]), axis=1)
    average_rouge_score = sum([score["rouge1"].fmeasure for score in scores]) / len(scores)
    print("Average ROUGE score: ", average_rouge_score)



if __name__ == "__main__":
    evaluate_visualizer()
    # evaluate_summarizer()