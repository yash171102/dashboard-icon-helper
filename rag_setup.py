

import os
import fitz  # PyMuPDF
import uuid
import re
import time
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# ---------- Configuration ----------
GEMINI_API_KEY = "AIzaSyCzaDBuV0n13yr5CVY9ZsmtpmU-QEpKJMY"
PDF_PATH = r"D:\car_telltale_bot\car_manuals\lum_thar_2009_uk.pdf"
FAISS_INDEX_PATH = r"D:\car_telltale_bot\vector_db\faiss.index"
TEXTS_PATH = r"D:\car_telltale_bot\vector_db\texts.pkl"
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

genai.configure(api_key=GEMINI_API_KEY)

# ---------- STEP 1: Extract Text from PDF ----------
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            full_text += text + "\n"
        if (i + 1) % 10 == 0 or (i + 1) == len(doc):
            print(f"✅ Extracted text from page {i+1}/{len(doc)}")
    return full_text

# ---------- STEP 2: Chunk Text ----------
def chunk_text(text, max_chunk_size=500):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks, chunk = [], ""
    for sentence in sentences:
        if len(chunk) + len(sentence) <= max_chunk_size:
            chunk += sentence + " "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + " "
    if chunk:
        chunks.append(chunk.strip())
    return chunks

# ---------- STEP 3: Create FAISS Index ----------
def create_faiss_index(pdf_path):
    print("📄 Reading PDF...")
    text = extract_text_from_pdf(pdf_path)

    print("🧱 Chunking text...")
    chunks = chunk_text(text)
    print(f"📦 Total chunks created: {len(chunks)}")

    print("⚙️ Generating embeddings...")
    embeddings = EMBED_MODEL.encode(chunks, show_progress_bar=True)
    embedding_dim = embeddings.shape[1]

    print("🗂️ Creating FAISS index...")
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(np.array(embeddings))

    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(TEXTS_PATH, 'wb') as f:
        pickle.dump(chunks, f)

    print("✅ FAISS index and texts saved.")
    return index, chunks

# ---------- STEP 4: Load FAISS Index ----------
def load_faiss_index():
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(TEXTS_PATH):
        return create_faiss_index(PDF_PATH)
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(TEXTS_PATH, 'rb') as f:
        texts = pickle.load(f)
    return index, texts

# ---------- STEP 5: Retrieve Context ----------
def retrieve_context(query, index, texts, top_k=5):
    query_embedding = EMBED_MODEL.encode([query])
    D, I = index.search(query_embedding, top_k)
    return [texts[i] for i in I[0]]

def ask_gemini(query, context_chunks, icon_desc=None):
    icon_section = f"Icon Description:\n{icon_desc}\n" if icon_desc else ""
    full_prompt = f"""
You are a car manual assistant. Use the following context from a car's user manual to answer the question.

{icon_section}
Context:
{chr(10).join(context_chunks)}

Question:
{query}
"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(full_prompt)
    return response.text.strip()

# ---------- MAIN CLI ----------
if __name__ == "__main__":
    index, texts = create_faiss_index(PDF_PATH)
    while True:
        query = input("\n❓ Ask your question (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break
        print("🔎 Retrieving context...")
        context = retrieve_context(query, index, texts)
        print("🤖 Asking Gemini...")
        answer = ask_gemini(query, context)
        print("\n🧠 Answer:")
        print(answer)
