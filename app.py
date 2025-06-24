

import streamlit as st
from PIL import Image
import io
import google.generativeai as genai
from rag_setup import retrieve_context, ask_gemini, load_faiss_index

# 🔑 Gemini API Key
GEMINI_API_KEY = "AIzaSyCzaDBuV0n13yr5CVY9ZsmtpmU-QEpKJMY"
genai.configure(api_key=GEMINI_API_KEY)

# 📚 FAISS Vector DB Load
faiss_index, context_texts = load_faiss_index()

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
    context_chunks = retrieve_context(icon_description, faiss_index, context_texts)

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

    follow_up_input = st.empty()

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

            st.components.v1.html(f"""
            <script>
            var synth = window.speechSynthesis;
            var utterThis = new SpeechSynthesisUtterance("{chat_answer.replace('"', '').replace("'", '')}");
            synth.speak(utterThis);
            </script>
            """, height=0)
