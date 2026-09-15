import os
import json
import numpy as np
import streamlit as st
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer, CrossEncoder
import google.generativeai as genai


# =====================================================
# 1. Configuration
# =====================================================

API_KEY = "+++++++++++++++++++"
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-3-flash-preview"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

llm = genai.GenerativeModel(MODEL_NAME)


# =====================================================
# 2. Load Models
# =====================================================

@st.cache_resource
def load_models():
    embed = SentenceTransformer(EMBEDDING_MODEL)
    reranker = CrossEncoder(RERANK_MODEL)
    return embed, reranker

embed_model, reranker_model = load_models()


# =====================================================
# 3. Intent Detection 
# =====================================================

def detect_intent(text):

    text = text.lower().strip()

    greetings = ["hello", "hi", "hey", "مرحبا", "bonjour"]
    goodbye = ["bye", "goodbye", "see you", "مع السلامة"]
    thanks = ["thanks", "thank you", "شكرا"]

    if text in greetings:
        return "greeting"

    if text in goodbye:
        return "goodbye"

    if text in thanks:
        return "thanks"

    return "medical_query"


def small_talk_response(intent):

    responses = {
        "greeting": "Hello 👋 I'm your Medical AI assistant. Ask me about patient history, diseases, medications or lab reports.",

        "goodbye": "Goodbye 👋 Feel free to come back if you need medical information.",

        "thanks": "You're welcome 😊"
    }

    return responses.get(intent)


# =====================================================
# 4. Build Vector Index
# =====================================================

@st.cache_resource
def build_index(_patients):

    all_chunks = []
    metadata = []

    for p in _patients:

        profile = f"""
        Patient Profile:
        Name: {p['first_name']} {p['last_name']}
        ID: {p['id']}
        Age: {p['age']}
        Disease: {p['disease']}
        Medication: {p['medication']}
        """

        all_chunks.append(profile)
        metadata.append({"source": "profile", "id": p["id"]})

        pdf_path = f"data/pdf_reports/patient_{p['id']}.pdf"

        if os.path.exists(pdf_path):

            try:
                reader = PdfReader(pdf_path)

                for i, page in enumerate(reader.pages):

                    text = page.extract_text() or ""

                    if len(text.strip()) > 20:

                        chunk = f"Lab Report Patient {p['id']} Page {i}: {text}"

                        all_chunks.append(chunk)
                        metadata.append({"source": f"pdf_page_{i}", "id": p["id"]})

            except Exception as e:
                print("PDF error:", e)

    embeddings = embed_model.encode(all_chunks)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))

    return index, all_chunks, metadata


# =====================================================
# 5. Retrieval + ReRanking
# =====================================================

def advanced_search(question, index, chunks, k=15):

    query_vec = embed_model.encode([question])

    D, I = index.search(np.array(query_vec).astype("float32"), k)

    results = [chunks[i] for i in I[0] if i < len(chunks)]

    pairs = [[question, r] for r in results]

    scores = reranker_model.predict(pairs)

    ranked = [r for _, r in sorted(zip(scores, results), reverse=True)]

    return "\n---\n".join(ranked[:5])


# =====================================================
# 6. Streamlit UI
# =====================================================

st.set_page_config(page_title="Medical RAG Assistant", layout="wide")

st.title(" Medical AI Assistant")


# =====================================================
# 7. Load Data
# =====================================================

with st.spinner("Loading Medical Knowledge Base..."):

    path = "data/patients.json"

    if os.path.exists(path):

        with open(path, encoding="utf-8") as f:
            patients = json.load(f)

        vector_index, text_chunks, meta = build_index(patients)

    else:

        st.error("patients.json not found")
        st.stop()


# =====================================================
# 8. Chat Memory
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =====================================================
# 9. User Input
# =====================================================

if prompt := st.chat_input("Ask about patients or lab results..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):

        response_placeholder = st.empty()
        full_response = ""

        intent = detect_intent(prompt)

        # -------- Small Talk --------

        if intent != "medical_query":

            full_response = small_talk_response(intent)
            response_placeholder.markdown(full_response)

        # -------- RAG --------

        else:

            context = advanced_search(prompt, vector_index, text_chunks)

            system_prompt = f"""
You are a professional Medical AI assistant.

Use ONLY the information from the provided context.

Rules:
- If the answer is not in the context say:
  "The information is not available in the medical records."
- Cite patient ID if possible.

CONTEXT:
{context}
"""

            res_stream = llm.generate_content(
                [system_prompt, prompt],
                stream=True
            )

            for chunk in res_stream:

                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)


    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )