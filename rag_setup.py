import os
import fitz  # PyMuPDF
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np

# ----- Constants -----
PDF_PATH = "car_manuals/lum_thar_2009_uk.pdf"  # Update if needed
FAISS_INDEX_PATH = "faiss_data/faiss_index.index"
TEXTS_PATH = "faiss_data/context_texts.pkl"

# ----- Step 1: Extract Text from PDF -----
def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at path: {pdf_path}")
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

# ----- Step 2: Chunking Text -----
def chunk_text(text, max_length=500):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1  # +1 for space
        if current_length >= max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# ----- Step 3: Create FAISS Index -----
def create_faiss_index(pdf_path):
    print("📄 Reading PDF...")
    text = extract_text_from_pdf(pdf_path)

    print("🧱 Chunking text...")
    chunks = chunk_text(text)

    print("🔍 Generating embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)

    print("🗂️ Creating FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    # Ensure faiss_data directory exists
    output_dir = os.path.dirname(FAISS_INDEX_PATH)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(TEXTS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("✅ FAISS index created and saved.")
    return index, chunks

# ----- Step 4: Load FAISS Index -----
def load_faiss_index():
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(TEXTS_PATH):
        return create_faiss_index(PDF_PATH)

    print("📦 Loading existing FAISS index and texts...")
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(TEXTS_PATH, "rb") as f:
        texts = pickle.load(f)
    return index, texts
