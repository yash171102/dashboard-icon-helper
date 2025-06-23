
# import os
# import fitz  # PyMuPDF
# import uuid
# import re
# import time
# import chromadb
# from sentence_transformers import SentenceTransformer

# import google.generativeai as genai


# GEMINI_API_KEY = "AIzaSyDzedkcJtR7qG-m1wloXpDcbD45MsDY810"
# genai.configure(api_key=GEMINI_API_KEY)


# # ---------- STEP 1: Extract Text from PDF ----------
# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     full_text = ""
#     for i, page in enumerate(doc):
#         text = page.get_text()
#         if text.strip():
#             full_text += text + "\n"
#         if (i + 1) % 10 == 0 or (i + 1) == len(doc):
#             print(f"✅ Extracted text from page {i+1}/{len(doc)}")
#     return full_text


# # ---------- STEP 2: Chunk Text ----------
# def chunk_text(text, max_chunk_size=500):
#     sentences = re.split(r'(?<=[.?!])\s+', text)
#     chunks, chunk = [], ""
#     for sentence in sentences:
#         if len(chunk) + len(sentence) <= max_chunk_size:
#             chunk += sentence + " "
#         else:
#             chunks.append(chunk.strip())
#             chunk = sentence + " "
#     if chunk:
#         chunks.append(chunk.strip())
#     return chunks


# # ---------- STEP 3: Create RAG Vector Index ----------
# def create_rag_index(pdf_path, collection_name="car_manual_kb"):
#     start_time = time.time()

#     print("📄 Reading PDF...")
#     text = extract_text_from_pdf(pdf_path)

#     print("🧱 Chunking text...")
#     chunks = chunk_text(text)
#     print(f"📦 Total chunks created: {len(chunks)}")

#     print("⚙️ Loading embedding model...")
#     model = SentenceTransformer("all-MiniLM-L6-v2")

#     print("🗂️ Initializing ChromaDB...")
#     chroma_client = chromadb.Client()
#     collection = chroma_client.get_or_create_collection(name=collection_name)

#     print("🔍 Generating embeddings in batches...")
#     batch_size = 32
#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]
#         embeddings = model.encode(batch).tolist()
#         ids = [str(uuid.uuid4()) for _ in batch]
#         collection.add(documents=batch, ids=ids, embeddings=embeddings)
#         print(f"✅ Processed batch {i + 1} to {i + len(batch)} of {len(chunks)}")

#     print(f"\n🎉 RAG index created successfully in {round(time.time() - start_time, 2)} seconds.")
#     return collection


# # ---------- STEP 4: Retrieve Relevant Chunks ----------
# def retrieve_context(query, collection, top_k=5):
#     model = SentenceTransformer("all-MiniLM-L6-v2")
#     query_embedding = model.encode(query).tolist()
#     results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
#     return results['documents'][0] if results['documents'] else []


# # ---------- STEP 5: Ask Google Gemini ----------
# def ask_gemini(query, context_chunks):
#     full_prompt = f"""
# You are a car manual assistant. Use the following context from a car's user manual to answer the question.

# Context:
# {chr(10).join(context_chunks)}

# Question:
# {query}
# """
#     model = genai.GenerativeModel('gemini-2.0-flash')
#     response = model.generate_content(full_prompt)
#     return response.text.strip()


# # ---------- MAIN FLOW ----------
# if __name__ == "__main__":
#     PDF_PATH = "C:/Users/user/Downloads/lum_thar_2009_uk.pdf"
#     COLLECTION_NAME = "car_manual_kb"

#     # Step 1-3: Create Index (do once)
#     collection = create_rag_index(PDF_PATH, COLLECTION_NAME)

#     # Step 4: Ask query
#     while True:
#         query = input("\n❓ Ask your question (or type 'exit'): ")
#         if query.lower() in ["exit", "quit"]:
#             break

#         print("🔎 Retrieving context...")
#         context = retrieve_context(query, collection)

#         print("🤖 Asking Gemini...")
#         answer = ask_gemini(query, context)
#         print("\n🧠 Answer:")
#         print(answer)







# import os
# import fitz  # PyMuPDF
# import uuid
# import re
# import time
# import chromadb
# from sentence_transformers import SentenceTransformer
# import google.generativeai as genai

# # 🔑 Gemini API Key
# GEMINI_API_KEY = "AIzaSyDzedkcJtR7qG-m1wloXpDcbD45MsDY810"
# genai.configure(api_key=GEMINI_API_KEY)

# # ---------- STEP 1: Extract Text from PDF ----------
# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     full_text = ""
#     for i, page in enumerate(doc):
#         text = page.get_text()
#         if text.strip():
#             full_text += text + "\n"
#         if (i + 1) % 10 == 0 or (i + 1) == len(doc):
#             print(f"✅ Extracted text from page {i+1}/{len(doc)}")
#     return full_text

# # ---------- STEP 2: Chunk Text ----------
# def chunk_text(text, max_chunk_size=500):
#     sentences = re.split(r'(?<=[.?!])\s+', text)
#     chunks, chunk = [], ""
#     for sentence in sentences:
#         if len(chunk) + len(sentence) <= max_chunk_size:
#             chunk += sentence + " "
#         else:
#             chunks.append(chunk.strip())
#             chunk = sentence + " "
#     if chunk:
#         chunks.append(chunk.strip())
#     return chunks

# # ---------- STEP 3: Create RAG Vector Index ----------
# def create_rag_index(pdf_path, collection_name="car_manual_kb"):
#     start_time = time.time()

#     print("📄 Reading PDF...")
#     text = extract_text_from_pdf(pdf_path)

#     print("🧱 Chunking text...")
#     chunks = chunk_text(text)
#     print(f"📦 Total chunks created: {len(chunks)}")

#     print("⚙️ Loading embedding model...")
#     model = SentenceTransformer("all-MiniLM-L6-v2")

#     print("🗂️ Initializing ChromaDB...")
#     chroma_client = chromadb.Client()
#     collection = chroma_client.get_or_create_collection(name=collection_name)

#     print("🔍 Generating embeddings...")
#     batch_size = 32
#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]
#         embeddings = model.encode(batch).tolist()
#         ids = [str(uuid.uuid4()) for _ in batch]
#         collection.add(documents=batch, ids=ids, embeddings=embeddings)
#         print(f"✅ Indexed batch {i + 1} to {i + len(batch)} of {len(chunks)}")

#     print(f"\n🎉 RAG index created successfully in {round(time.time() - start_time, 2)} seconds.")
#     return collection

# # ---------- STEP 4: Retrieve Relevant Chunks ----------
# def retrieve_context(query, collection, top_k=5):
#     model = SentenceTransformer("all-MiniLM-L6-v2")
#     query_embedding = model.encode(query).tolist()
#     results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
#     return results['documents'][0] if results['documents'] else []

# # ---------- STEP 5: Ask Gemini with Context-Aware Prompt ----------
# def ask_gemini(query, context_chunks, icon_desc=None):
#     model = genai.GenerativeModel('gemini-2.0-flash')

#     prompt = f"""
# You are an expert assistant for car dashboard icons. A user is asking about a warning light using this context.

# 🔧 Icon Description:
# "{icon_desc or 'Not provided'}"

# 📖 Car Manual Snippets:
# "{chr(10).join(context_chunks)}"

# 💬 User Question:
# "{query}"

# Reply precisely, clearly, and only based on the car manual context. If no exact solution is found, explain that. Avoid asking the user to repeat or re-describe the icon.
# """

#     response = model.generate_content(prompt)
#     return response.text.strip()

# # ---------- MAIN FLOW ----------
# if __name__ == "__main__":
#     PDF_PATH = "C:/Users/user/Downloads/lum_thar_2009_uk.pdf"
#     COLLECTION_NAME = "car_manual_kb"

#     collection = create_rag_index(PDF_PATH, COLLECTION_NAME)

#     while True:
#         query = input("\n❓ Ask your question (or type 'exit'): ")
#         if query.lower() in ["exit", "quit"]:
#             break

#         context = retrieve_context(query, collection)
#         answer = ask_gemini(query, context)
#         print("\n🧠 Answer:")
#         print(answer)



import os
import fitz  # PyMuPDF
import uuid
import re
import time
import chromadb
from chromadb.config import Settings
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# ---------- Configuration ----------
GEMINI_API_KEY = "AIzaSyDzedkcJtR7qG-m1wloXpDcbD45MsDY810"
PDF_PATH = r"D:\car_telltale_bot\car_manuals\lum_thar_2009_uk.pdf"
PERSIST_DIRECTORY = r"D:\car_telltale_bot\vector_db"
COLLECTION_NAME = "car_manual_kb"

genai.configure(api_key=GEMINI_API_KEY)


# ---------- STEP 1: Extract Text from PDF ----------
def extract_text_from_pdf(pdf_path):
    """Extracts all text from a given PDF file using PyMuPDF."""
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
    """Splits the text into smaller chunks based on sentence boundaries."""
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


# ---------- STEP 3: Create RAG Vector Index ----------
def create_rag_index(pdf_path, collection_name=COLLECTION_NAME):
    """Creates a ChromaDB vector store with SentenceTransformer embeddings."""
    start_time = time.time()

    print("📄 Reading PDF...")
    text = extract_text_from_pdf(pdf_path)

    print("🧱 Chunking text...")
    chunks = chunk_text(text)
    print(f"📦 Total chunks created: {len(chunks)}")

    print("⚙️ Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("🗂️ Initializing ChromaDB (persistent)...")
    chroma_client = PersistentClient(path=PERSIST_DIRECTORY)
    collection = chroma_client.get_or_create_collection(name=collection_name)

    print("🔍 Generating embeddings in batches...")
    batch_size = 32
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        embeddings = model.encode(batch).tolist()
        ids = [str(uuid.uuid4()) for _ in batch]
        collection.add(documents=batch, ids=ids, embeddings=embeddings)
        print(f"✅ Processed batch {i + 1} to {i + len(batch)} of {len(chunks)}")

    print(f"\n🎉 RAG index created successfully in {round(time.time() - start_time, 2)} seconds.")
    return collection


# ---------- STEP 4: Retrieve Relevant Chunks ----------
def retrieve_context(query, collection, top_k=5):
    """Retrieves top-k relevant chunks using cosine similarity from ChromaDB."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results['documents'][0] if results['documents'] else []


def ask_gemini(query, context_chunks, icon_desc=None):
    """Uses Gemini to answer a question using manual context (RAG) and optional icon description."""
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



# ---------- MAIN FLOW (Optional CLI) ----------
if __name__ == "__main__":
    collection = create_rag_index(PDF_PATH, COLLECTION_NAME)

    while True:
        query = input("\n❓ Ask your question (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break

        print("🔎 Retrieving context...")
        context = retrieve_context(query, collection)

        print("🤖 Asking Gemini...")
        answer = ask_gemini(query, context)
        print("\n🧠 Answer:")
        print(answer)
