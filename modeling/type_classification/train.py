import pandas as pd
import torch
import transformers
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
from transformers import DistilBertModel, DistilBertTokenizer
from sklearn import metrics
from tqdm import tqdm
import numpy as np
import re
from transformers import AutoModelForSequenceClassification
import torch
from sklearn.model_selection import train_test_split
from transformers import DistilBertForSequenceClassification
from transformers import TrainingArguments
from transformers import Trainer
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification, AutoModel

# Setting up the device for GPU usage
from torch import cuda


class GDELTDataset(Dataset):
    def __init__(self, data, max_len, tokenizer):
        self.texts = data['ARTICLETEXT'].values
        self.labels = data['EventCode'].values
        self.max_len = max_len
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = self.tokenizer(text, truncation=True, padding='max_length', max_length=self.max_len, return_tensors='pt')
        return {
            'input_ids': encoding['input_ids'][0],
            'attention_mask': encoding['attention_mask'][0],
            'label': torch.tensor(label, dtype=torch.long)
        }


def train_bert(df, n_labels, device):

    tokenizer = AutoTokenizer.from_pretrained('google-bert/bert-base-uncased')
    model = AutoModelForSequenceClassification.from_pretrained("google-bert/bert-base-uncased")
    model.to(device)

    max_len = 26
    dataset = GDELTDataset(df, max_len, tokenizer)
    train, val = train_test_split(dataset, test_size=0.1)
    train_dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
    val_dataloader = DataLoader(val, batch_size=4, shuffle=True)

    input_ids = torch.stack([d['input_ids'] for d in train], dim=0).to(device)
    print(input_ids.shape)
    # attention_mask = torch.tensor([d['attention_mask'] for d in train]).to(device)

    # pred1 = model(input_ids, output_hidden_states=True)

    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='f1',
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train,
        eval_dataset=val,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    eval_result = trainer.evaluate()
    print(f"Accuracy: {eval_result['eval_accuracy']}")
    print(f"F1-score: {eval_result['eval_f1']}")



def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    accuracy = metrics.accuracy_score(y_true=labels, y_pred=predictions)
    f1 = metrics.f1_score(y_true=labels, y_pred=predictions, average='macro')
    return {'accuracy': accuracy, 'f1': f1}


if __name__ == "__main__":
    df = pd.read_csv("bq-results-scraped.csv")
    df = df.dropna(subset=["ARTICLETEXT"])

    # Preprocessing steps
    html=re.compile(r'<.*?>')
    df['ARTICLETEXT'] = df['ARTICLETEXT'].apply(lambda x: html.sub(r'', x))
    num_labels = len(df['EventCode'].unique())

    device = 'cuda' if cuda.is_available() else 'cpu'
    train_bert(df, num_labels, device)