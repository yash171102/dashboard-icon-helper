import os
import fitz  # PyMuPDF
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# ---------- Constants ----------
PDF_PATH = "car_manuals/lum_thar_2009_uk.pdf"  # Adjust path if needed
FAISS_INDEX_PATH = "faiss_data/faiss_index.index"
TEXTS_PATH = "faiss_data/context_texts.pkl"
EMBED_MOD = "all-MiniLM-L6-v2"  # ✅ Embedding model name

# ---------- Step 1: Extract Text from PDF ----------
def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"🚫 PDF file not found at: {pdf_path}")
    doc = fitz.open(pdf_path)
    full_text = ""
    for i, page in enumerate(doc):
        full_text += page.get_text()
        if (i + 1) % 10 == 0 or (i + 1) == len(doc):
            print(f"✅ Extracted text from page {i+1}/{len(doc)}")
    return full_text

# ---------- Step 2: Chunk Text ----------
def chunk_text(text, max_length=500):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length >= max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    print(f"📦 Total chunks created: {len(chunks)}")
    return chunks

# ---------- Step 3: Create FAISS Index ----------
def create_faiss_index(pdf_path):
    print("📄 Reading PDF...")
    text = extract_text_from_pdf(pdf_path)

    print("🧱 Chunking text...")
    chunks = chunk_text(text)

    print("⚙️ Generating embeddings...")
    model = SentenceTransformer(EMBED_MOD)
    embeddings = model.encode(chunks)

    print("🗂️ Creating FAISS index...")
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(np.array(embeddings))

    dir_path = os.path.dirname(FAISS_INDEX_PATH)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(TEXTS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("✅ FAISS index created and saved.")
    return index, chunks

# ---------- Step 4: Load FAISS Index ----------
def load_faiss_index():
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(TEXTS_PATH):
        return create_faiss_index(PDF_PATH)

    print("📥 Loading existing FAISS index and context...")
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(TEXTS_PATH, "rb") as f:
        texts = pickle.load(f)
    return index, texts

# ---------- Step 5: Retrieve Context ----------
def retrieve_context(query, faiss_index, context_texts, top_k=5):
    model = SentenceTransformer(EMBED_MOD)
    query_embedding = model.encode([query])
    D, I = faiss_index.search(np.array(query_embedding), top_k)
    results = [context_texts[i] for i in I[0]]
    return "\n".join(results)

# ---------- Step 6: Ask Gemini ----------
def ask_gemini(prompt, model_name="models/gemini-1.5-flash"):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text.strip()
