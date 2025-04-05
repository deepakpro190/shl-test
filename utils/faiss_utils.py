import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
import os
import glob

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index
faiss_index = faiss.IndexFlatL2(384)

# Store tuples of (text, link)
stored_texts = []

# ✅ Store CSV data into FAISS
def store_results_to_faiss():
    global stored_texts, faiss_index

    stored_texts.clear()
    faiss_index.reset()

    for file in glob.glob("data/*.csv"):
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            text = f"{row['Job Title']} | Remote: {row['Remote Testing']} | Adaptive: {row['Adaptive/IRT']} | Keys: {row.get('Keys', '')}"
            embedding = model.encode([text]).astype("float32")
            faiss_index.add(embedding)
            stored_texts.append((text, row.get("Link", "#")))

# ✅ Query FAISS index
def query_faiss(query, k=5):
    query_vector = model.encode([query]).astype("float32")
    D, I = faiss_index.search(query_vector, k)

    results = []
    for idx in I[0]:
        if 0 <= idx < len(stored_texts):
            text, link = stored_texts[idx]
            results.append((text, link))
    return results
