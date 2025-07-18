import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import torch
import faiss
import numpy as np

# Load knowledge base
df = pd.read_csv(r'C:\Users\deepak\Pictures\trading\output.csv')  # Columns: 'Sloka', 'Translation'
df['document'] = df['translation']

# Load sentence encoder (for retriever)
retriever_model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode KB
kb_embeddings = retriever_model.encode(df['document'].tolist(), convert_to_numpy=True)

# Create FAISS index
index = faiss.IndexFlatL2(kb_embeddings.shape[1])
index.add(kb_embeddings)

# Load BERT model for NLI (True/False decision)
nli_model = BertForSequenceClassification.from_pretrained('ynie/roberta-large-snli_mnli_fever_anli_R1_R2_R3-nli')
tokenizer = BertTokenizer.from_pretrained('roberta-base')

labels_map = {0: "entailment", 1: "neutral", 2: "contradiction"}

def classify_entailment(premise, hypothesis):
    inputs = tokenizer(premise, hypothesis, return_tensors='pt', truncation=True, padding=True)
    outputs = nli_model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    label_id = torch.argmax(probs).item()
    return labels_map[label_id], float(probs[0][label_id])

def rag_fact_check(query, top_k=3, threshold=0.9):
    query_vec = retriever_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_vec, top_k)

    for idx in I[0]:
        doc = df.iloc[idx]['document']
        label, confidence = classify_entailment(doc, query)
        if label == 'entailment' and confidence >= threshold:
            return "True", doc, confidence

    return "False", None, None

# 🔍 Example
query = "Krishna advises Arjuna to focus on duty without attachment to results"
result, support_doc, confidence = rag_fact_check(query)

print(f"Prediction: {result}")
if result == "True":
    print(f"Supported by: {support_doc}\nConfidence: {confidence:.4f}")
