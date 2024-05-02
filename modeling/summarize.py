from mmif import Mmif, View, AnnotationTypes, DocumentTypes
from transformers import pipeline
from tqdm import tqdm
import torch
import math
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import TrainingArguments, Trainer
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from nltk.tokenize import sent_tokenize
import numpy as np
import networkx as nx
from summarizer import Summarizer

tqdm.pandas()

# TEST_DOCUMENT = "../mmif_files/whisper3.mmif"
MAX_LEN = 1024
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")
print(f"Using {device}")
summarizer = pipeline(
    "summarization", model="facebook/bart-large-cnn", device=device)

# model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-xsum-12-6")
# tokenizer = BartTokenizer.from_pretrained("sshleifer/distilbart-xsum-12-6")


def url2posix(path):
    if path.startswith('file:///'):
        path = path[7:]
    return path

# TODO: Error handling

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


def summarize_from_text(asr_text: View):
    if len(asr_text) > MAX_LEN:
        chunks = [asr_text[i:i+MAX_LEN]
                  for i in range(0, len(asr_text), MAX_LEN)]
        summaries = [generate_abstractive_summary(chunk, max_len=int(
            math.floor(MAX_LEN/len(chunks)))) for chunk in tqdm(chunks)]
        asr_text = " ".join(summaries)
    return generate_abstractive_summary(asr_text), asr_text


def generate_abstractive_summary(asr_text: str, max_len=150):
    min_len = 30 if max_len > 30 else int(max_len/2)
    return summarizer(asr_text, max_length=max_len, min_length=min_len, do_sample=False)[0]['summary_text']


def summarize_file(mmif: Mmif):
    gold_transcript = get_transcript(mmif)
    if gold_transcript:
        asr_text = gold_transcript
    else:
        asr_views = get_asr_views(mmif)
        asr_text = get_asr_text(asr_views[0])
    summary, long_summary = summarize_from_text(asr_text)
    return summary, long_summary, asr_text


def fine_tune():
    df = pd.read_csv("../data/descriptions.csv")
    print("Performing extractive summarization")
    extractive_model = Summarizer()
    df["description"] = df["description"].progress_apply(lambda x: extractive_model(x))

    train, test = train_test_split(df)
    print("Tokenizing summaries...")
    train_summaries = summarizer.tokenizer(train["description"].tolist())
    test_summaries = summarizer.tokenizer(test["description"].tolist())
    print("Tokenizing transcripts...")
    train_transcripts = summarizer.tokenizer(train["transcript"].tolist())
    test_transcripts = summarizer.tokenizer(test["transcript"].tolist())

    class AAPBDataset(torch.utils.data.Dataset):
        def __init__(self, transcripts, summaries):
            self.transcripts = transcripts
            self.summaries = summaries

        def __getitem__(self, idx):
            return {"input_ids": torch.tensor(self.transcripts.input_ids[idx], dtype=torch.long),
                    "attention_mask": torch.tensor(self.transcripts.attention_mask[idx], dtype=torch.long),
                    "decoder_input_ids": torch.tensor(self.summaries.input_ids[idx], dtype=torch.long),
                    "decoder_attention_mask": torch.tensor(self.summaries.attention_mask[idx], dtype=torch.long)}

        def __len__(self):
            return len(self.transcripts.input_ids)
        
    train_encodings = AAPBDataset(train_transcripts, train_summaries)
    test_encodings = AAPBDataset(test_transcripts, test_summaries)

    training_args = TrainingArguments(
        output_dir="../models/aapb_summarizer",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="../logs",
        logging_steps=10,
        save_steps=10,
        eval_steps=10,
        evaluation_strategy="steps",
        report_to="tensorboard",
        run_name="aapb_summarizer"
    )

    trainer = Trainer(
        model=summarizer.model,
        args=training_args,
        train_dataset=train_encodings,
        eval_dataset=test_encodings
    )

    print("Training...")
    trainer.train()
    trainer.save_model("../models/aapb_summarizer")


if __name__ == "__main__":
    fine_tune()
