from mmif import Mmif, View, AnnotationTypes, DocumentTypes
from transformers import pipeline
from tqdm import tqdm
import torch
import math

# TEST_DOCUMENT = "../mmif_files/whisper3.mmif"
MAX_LEN = 1024
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")
print(device)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)

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
        chunks = [asr_text[i:i+MAX_LEN] for i in range(0, len(asr_text), MAX_LEN)]
        summaries = [generate_abstractive_summary(chunk, max_len=int(math.floor(MAX_LEN/len(chunks)))) for chunk in tqdm(chunks)]
        asr_text = " ".join(summaries)
    return generate_abstractive_summary(asr_text)

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
    summary = summarize_from_text(asr_text)
    return summary, asr_text
