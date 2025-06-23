# import streamlit as st
# from modules.detect_icon import detect_icon_label
# from modules.query_manual import query_manual
# from modules.llm_response import get_llm_response

# st.set_page_config(page_title="Car Telltale Support Bot")
# st.title("🚘 Car Telltale Support Assistant")

# option = st.radio("Choose input type:", ("Upload Image", "Describe Icon"))
# user_query = ""

# if option == "Upload Image":
#     image = st.file_uploader("Upload an image of the telltale icon:", type=["jpg", "jpeg", "png"])
#     if image:
#         label = detect_icon_label(image)
#         st.success(f"Detected icon: {label}")
#         user_query = f"What does the '{label}' icon mean?"

# else:
#     description = st.text_input("Describe the icon (e.g., 'battery symbol with plus sign')")
#     if description:
#         user_query = f"The user describes the icon as: {description}"

# if user_query:
#     context = query_manual(user_query)
#     response = get_llm_response(user_query, context)
#     st.markdown("### 📘 Car Manual Info")
#     st.info(context)
#     st.markdown("### 🤖 Assistant Response")
#     st.success(response)













# import os
# import fitz
# import uuid
# import re
# import time
# import streamlit as st
# import chromadb
# from PIL import Image
# from dotenv import load_dotenv
# from sentence_transformers import SentenceTransformer
# import google.generativeai as genai

# GEMINI_API_KEY = "AIzaSyDzedkcJtR7qG-m1wloXpDcbD45MsDY810"
# genai.configure(api_key=GEMINI_API_KEY)

# # Load embedding model once
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# # Load ChromaDB collection
# chroma_client = chromadb.Client()
# collection = chroma_client.get_or_create_collection("car_manual_kb")


# def retrieve_context(query, top_k=5):
#     query_embedding = embedding_model.encode(query).tolist()
#     results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
#     return results['documents'][0] if results['documents'] else []


# def ask_gemini_text(question, context_chunks):
#     prompt = f"""You are a car dashboard assistant. Use the following context to answer the user's query.

# Context:
# {chr(10).join(context_chunks)}

# Question:
# {question}
# """
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     response = model.generate_content(prompt)
#     return response.text.strip()


# def ask_gemini_image(image_file):
#     img = Image.open(image_file)
#     model = genai.GenerativeModel("models/gemini-1.5-flash")  # Updated model name

#     # Convert image to bytes
#     import io
#     image_bytes = io.BytesIO()
#     img.save(image_bytes, format="PNG")
#     image_bytes.seek(0)

#     # Generate response
#     response = model.generate_content(
#         contents=[
#             {
#                 "role": "user",
#                 "parts": [
#                     {
#                         "inline_data": {
#                             "mime_type": "image/png",
#                             "data": image_bytes.read()
#                         }
#                     },
#                     {"text": "Describe what this icon represents in the context of a car dashboard."}
#                 ]
#             }
#         ]
#     )
#     return response.text.strip()



# # ---------- Streamlit UI ----------
# st.set_page_config(page_title="Car Icon Assistant", layout="centered")
# st.title("🚘 Car Telltale Icon Assistant")
# st.markdown("Describe a car dashboard icon or upload its image to understand its meaning from your car's manual.")

# option = st.radio("Choose Input Method", ("Text Description", "Upload Image"))

# user_query = None

# if option == "Text Description":
#     user_query = st.text_input("📝 Describe the icon (e.g., 'triangle with exclamation')")

# elif option == "Upload Image":
#     uploaded_image = st.file_uploader("📷 Upload an icon image", type=["jpg", "jpeg", "png"])
#     if uploaded_image:
#         with st.spinner("🤖 Analyzing image..."):
#             icon_description = ask_gemini_image(uploaded_image)
#             st.success("🧠 Detected: " + icon_description)
#             user_query = icon_description

# if user_query:
#     if st.button("🔍 Get Info"):
#         with st.spinner("📚 Retrieving context from manual..."):
#             context = retrieve_context(user_query)

#         with st.spinner("🤖 Asking Gemini..."):
#             answer = ask_gemini_text(user_query, context)

#         st.markdown("### 💬 Answer")
#         st.write(answer)






# import streamlit as st
# from PIL import Image
# import io
# import os
# import google.generativeai as genai
# from rag_setup import retrieve_context, ask_gemini
# import chromadb

# # 🔑 Gemini API Key
# GEMINI_API_KEY = "AIzaSyDzedkcJtR7qG-m1wloXpDcbD45MsDY810"
# genai.configure(api_key=GEMINI_API_KEY)

# # 📚 Collection Name
# COLLECTION_NAME = "car_manual_kb"

# # 🔁 Load ChromaDB Collection (from persistent location if needed)
# chroma_client = chromadb.Client()
# collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# # 🔍 Load Gemini Vision Model
# vision_model = genai.GenerativeModel("models/gemini-1.5-flash")

# # 🔎 Extract Description + RAG Answer
# def describe_icon_and_fetch_answer(image_file):
#     image = Image.open(image_file)

#     image_bytes = io.BytesIO()
#     image.save(image_bytes, format="PNG")
#     image_bytes.seek(0)

#     # Step 1: Ask Gemini Vision to describe the icon
#     gemini_response = vision_model.generate_content(
#         contents=[
#             {
#                 "role": "user",
#                 "parts": [
#                     {
#                         "inline_data": {
#                             "mime_type": "image/png",
#                             "data": image_bytes.read()
#                         }
#                     },
#                     {"text": "Describe this car dashboard icon."}
#                 ]
#             }
#         ]
#     )

#     icon_description = gemini_response.text.strip()

#     # Step 2: Retrieve context from manual using RAG
#     context_chunks = retrieve_context(icon_description, collection)

#     # Step 3: Ask Gemini with manual context
#     answer = ask_gemini(icon_description, context_chunks)

#     return icon_description, context_chunks, answer


# # -------------------- Streamlit UI --------------------

# st.set_page_config(page_title="Car Dashboard Icon Helper", layout="wide")
# st.title("🚗 Car Dashboard Icon Assistant (with Gemini + RAG)")

# uploaded_image = st.file_uploader("📤 Upload a car dashboard icon (image)", type=["jpg", "png", "jpeg"])

# if uploaded_image is not None:
#     st.image(uploaded_image, caption="Uploaded Icon", use_column_width=True)

#     with st.spinner("🔍 Understanding the icon and searching the manual..."):
#         icon_description, context_chunks, answer = describe_icon_and_fetch_answer(uploaded_image)

#     st.markdown("### 🧠 Gemini Icon Description")
#     st.info(icon_description)

#     st.markdown("### 📖 Car Manual-based Answer")
#     st.success(answer)

#     st.markdown("---")
#     st.markdown("### 💬 Ask Follow-up Questions (RAG-powered)")
#     follow_up = st.text_input("Type your question about this icon or car feature:")

#     if follow_up:
#         with st.spinner("Searching manual and asking Gemini..."):
#             context = retrieve_context(follow_up, collection)
#             chat_answer = ask_gemini(follow_up, context)
#             st.markdown("#### 🧠 Gemini Answer")
#             st.write(chat_answer)





# import streamlit as st
# from PIL import Image
# import io
# import chromadb
# import google.generativeai as genai
# from rag_setup import retrieve_context, ask_gemini

# # 🔑 Gemini API Key
# GEMINI_API_KEY = "AIzaSyDzedkcJtR7qG-m1wloXpDcbD45MsDY810"
# genai.configure(api_key=GEMINI_API_KEY)

# # 📚 ChromaDB Collection
# COLLECTION_NAME = "car_manual_kb"
# chroma_client = chromadb.Client()
# collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# # 🔍 Load Gemini Vision Model
# vision_model = genai.GenerativeModel("models/gemini-1.5-flash")

# # 📸 Describe Icon + Fetch RAG Answer
# def describe_icon_and_fetch_answer(image_file):
#     image = Image.open(image_file)
#     image_bytes = io.BytesIO()
#     image.save(image_bytes, format="PNG")
#     image_bytes.seek(0)

#     # Step 1: Describe icon
#     gemini_response = vision_model.generate_content(
#         contents=[
#             {
#                 "role": "user",
#                 "parts": [
#                     {"inline_data": {"mime_type": "image/png", "data": image_bytes.read()}},
#                     {"text": "Describe this car dashboard icon."}
#                 ]
#             }
#         ]
#     )

#     icon_description = gemini_response.text.strip()

#     # Step 2: Get manual context
#     context_chunks = retrieve_context(icon_description, collection)

#     # Step 3: Ask Gemini
#     answer = ask_gemini(icon_description, context_chunks, icon_desc=icon_description)

#     return icon_description, context_chunks, answer

# # -------------------- Streamlit UI --------------------
# st.set_page_config(page_title="Car Dashboard Icon Helper", layout="wide")
# st.title("🚗 Car Dashboard Icon Assistant")

# uploaded_image = st.file_uploader("📤 Upload a dashboard icon (image)", type=["jpg", "png", "jpeg"])

# if uploaded_image:
#     st.image(uploaded_image, caption="Uploaded Icon", use_column_width=True)

#     with st.spinner("🔍 Understanding the icon and reading the manual..."):
#         icon_desc, context_chunks, answer = describe_icon_and_fetch_answer(uploaded_image)
#         st.session_state.icon_desc = icon_desc
#         st.session_state.manual_context = context_chunks

#     st.markdown("### 🧠 Icon Description")
#     st.info(icon_desc)

#     # st.markdown("### 📖 Car Manual-based Answer")
#     # st.success(answer)

#     st.markdown("---")
#     st.markdown("### 💬 Ask Follow-up Questions (Based on This Icon)")

#     follow_up = st.text_input("Ask about this warning light (e.g., what to do, can I drive?)")
#     if follow_up:
#         with st.spinner("🔁 Retrieving Answer with manual context..."):
#             chat_answer = ask_gemini(follow_up, st.session_state.manual_context, icon_desc=st.session_state.icon_desc)
#             st.markdown("#### 🧠 Follow-up Answer")
#             st.write(chat_answer)





# import streamlit as st
# from PIL import Image
# import io
# import chromadb
# import google.generativeai as genai
# from rag_setup import retrieve_context, ask_gemini

# # 🔑 Gemini API Key
# GEMINI_API_KEY = "AIzaSyDzedkcJtR7qG-m1wloXpDcbD45MsDY810"
# genai.configure(api_key=GEMINI_API_KEY)

# # 📚 ChromaDB Collection
# COLLECTION_NAME = "car_manual_kb"
# chroma_client = chromadb.Client()
# collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# # 🔍 Load Gemini Vision Model
# vision_model = genai.GenerativeModel("models/gemini-1.5-flash")

# # 📸 Describe Icon + Fetch RAG Answer
# def describe_icon_and_fetch_answer(image_file):
#     image = Image.open(image_file)
#     image_bytes = io.BytesIO()
#     image.save(image_bytes, format="PNG")
#     image_bytes.seek(0)

#     # Step 1: Describe icon
#     gemini_response = vision_model.generate_content(
#         contents=[
#             {
#                 "role": "user",
#                 "parts": [
#                     {"inline_data": {"mime_type": "image/png", "data": image_bytes.read()}},
#                     {"text": "Describe this car dashboard icon."}
#                 ]
#             }
#         ]
#     )

#     icon_description = gemini_response.text.strip()

#     # Step 2: Get manual context
#     context_chunks = retrieve_context(icon_description, collection)

#     # Step 3: Ask Gemini
#     answer = ask_gemini(icon_description, context_chunks, icon_desc=icon_description)

#     return icon_description, context_chunks, answer

# # -------------------- Streamlit UI --------------------
# st.set_page_config(page_title="Car Dashboard Icon Helper", layout="wide")
# st.title("🚗 Car Dashboard Icon Assistant")

# st.markdown("""
# ### 📸 Upload or Take a Photo of a Dashboard Icon

# - On **mobile**, tap **"Browse files"** below and select **"Camera"** if available.
# - Your phone's browser will prompt you to **take a new photo** or **choose from gallery**.

# """)

# # 🔼 Standard Streamlit uploader
# uploaded_image = st.file_uploader("Upload image (JPG, PNG, JPEG)", type=["jpg", "jpeg", "png"])

# if uploaded_image:
#     st.image(uploaded_image, caption="Uploaded Icon", use_column_width=True)

#     with st.spinner("🔍 Understanding the icon and reading the manual..."):
#         icon_desc, context_chunks, answer = describe_icon_and_fetch_answer(uploaded_image)
#         st.session_state.icon_desc = icon_desc
#         st.session_state.manual_context = context_chunks

#     st.markdown("### 🧠 Icon Description")
#     st.info(icon_desc)

#     st.markdown("### 📖 Car Manual-based Answer")
#     st.success(answer)

#     st.markdown("---")
#     st.markdown("### 💬 Ask Follow-up Questions")

#     follow_up = st.text_input("Ask about this warning light (e.g., what to do, can I drive?)")
#     if follow_up:
#         with st.spinner("🔁 Retrieving Answer with manual context..."):
#             chat_answer = ask_gemini(follow_up, st.session_state.manual_context, icon_desc=st.session_state.icon_desc)
#             st.markdown("#### 🧠 Follow-up Answer")
#             st.write(chat_answer)

# # Optional: Custom HTML camera uploader (non-functional unless extended with JS + base64 handling)
# with st.expander("📷 Trouble using mobile camera? Try this (advanced browser support only)"):
#     st.markdown("""
#     If your browser doesn't show a camera option above, try this:
#     """)
#     st.components.v1.html("""
#     <input type="file" accept="image/*" capture="environment" style="font-size: 18px; margin-top: 10px;">
#     """, height=50)
#     st.caption("Note: This does not send the image to Streamlit directly — it's for demo purposes only.")







import streamlit as st
from PIL import Image
import io
import chromadb
import google.generativeai as genai
from rag_setup import retrieve_context, ask_gemini

# 🔑 Gemini API Key
GEMINI_API_KEY = "AIzaSyDzedkcJtR7qG-m1wloXpDcbD45MsDY810"
genai.configure(api_key=GEMINI_API_KEY)

# 📚 ChromaDB Collection
COLLECTION_NAME = "car_manual_kb"
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# 🔍 Load Gemini Vision Model
vision_model = genai.GenerativeModel("models/gemini-1.5-flash")

# 📸 Describe Icon + Fetch RAG Answer
def describe_icon_and_fetch_answer(image_file):
    image = Image.open(image_file)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    # Step 1: Describe icon
    gemini_response = vision_model.generate_content(
        contents=[
            {
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": "image/png", "data": image_bytes.read()}},
                    {"text": "Describe this car dashboard icon."}
                ]
            }
        ]
    )

    icon_description = gemini_response.text.strip()

    # Step 2: Get manual context
    context_chunks = retrieve_context(icon_description, collection)

    # Step 3: Ask Gemini
    answer = ask_gemini(icon_description, context_chunks, icon_desc=icon_description)

    return icon_description, context_chunks, answer

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Car Dashboard Icon Helper", layout="wide")
st.title("🚗 Car Dashboard Icon Assistant")

st.markdown("""
### 📸 Upload or Take a Photo of a Dashboard Icon

- On **mobile**, tap **"Browse files"** and choose **"Camera"**.
- We'll analyze the icon and give you an answer from the manual.
""")

uploaded_image = st.file_uploader("Upload image (JPG, PNG, JPEG)", type=["jpg", "jpeg", "png"])

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Icon", use_column_width=True)

    with st.spinner("🔍 Understanding the icon and reading the manual..."):
        icon_desc, context_chunks, answer = describe_icon_and_fetch_answer(uploaded_image)
        st.session_state.icon_desc = icon_desc
        st.session_state.manual_context = context_chunks

    st.markdown("### 🧠 Icon Description")
    st.info(icon_desc)

    st.markdown("### 📖 Car Manual-based Answer")
    st.success(answer)

    # 🔊 Speak the initial answer aloud
    st.components.v1.html(f"""
    <script>
    var synth = window.speechSynthesis;
    var utterThis = new SpeechSynthesisUtterance("{answer.replace('"', '').replace("'", '')}");
    synth.speak(utterThis);
    </script>
    """, height=0)

    st.markdown("---")
    st.markdown("### 💬 Ask Follow-up Questions (Text or Voice)")

    # Voice-to-text + text input
    follow_up_input = st.empty()

    # Voice recognition button (JavaScript in browser)
    st.components.v1.html("""
    <script>
      const streamlitInput = window.parent.document.querySelector('iframe').contentWindow;
      function startListening() {
        var recognition = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            window.parent.postMessage({type: "streamlit:setComponentValue", value: transcript}, "*");
        };
        recognition.onerror = function(event) {
            alert("Voice input error: " + event.error);
        };
        recognition.start();
      }
    </script>
    <button onclick="startListening()" style="font-size:16px;padding:10px 15px;margin:10px 0;">
      🎙️ Speak Your Question
    </button>
    """, height=80)

    follow_up = follow_up_input.text_input("You can also type your follow-up here:")

    if follow_up:
        with st.spinner("🔁 Getting response..."):
            chat_answer = ask_gemini(follow_up, st.session_state.manual_context, icon_desc=st.session_state.icon_desc)

            st.markdown("#### 🧠 Follow-up Answer")
            st.write(chat_answer)

            # 🔊 Speak the follow-up answer aloud
            st.components.v1.html(f"""
            <script>
            var synth = window.speechSynthesis;
            var utterThis = new SpeechSynthesisUtterance("{chat_answer.replace('"', '').replace("'", '')}");
            synth.speak(utterThis);
            </script>
            """, height=0)
