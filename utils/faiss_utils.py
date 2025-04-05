import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
import os
import glob

model = SentenceTransformer("all-MiniLM-L6-v2")
faiss_index = faiss.IndexFlatL2(384)
stored_texts = []

def store_results_to_faiss():
    global stored_texts
    stored_texts.clear()
    faiss_index.reset()

    for file in glob.glob("data/*.csv"):
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            text = f"{row['Job Title']} | Remote: {row['Remote Testing']} | Adaptive: {row['Adaptive/IRT']} | Keys: {row.get('Keys', '')}"
            embedding = model.encode([text])
            faiss_index.add(embedding)
            stored_texts.append((text, row.get("Link", "#")))

def query_faiss(query, k=5):
    # Step 1: Convert query to vector
    query_vector = embedder.encode([query]).astype('float32')
    
    # Step 2: Perform search
    D, I = index.search(query_vector, k)

    results = []
    for idx in I[0]:
        if 0 <= idx < len(stored_texts):
            text, link = stored_texts[idx]
            results.append((text, link))
    return results


def init_faiss():
    faiss_index.reset()
    stored_texts.clear()
