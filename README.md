# 🩺 Medical RAG Assistant using Gemini API

> A Retrieval-Augmented Generation (RAG) system for querying synthetic medical records using semantic search, document re-ranking, and the Gemini API.

---



https://github.com/user-attachments/assets/bf3a06ed-186f-4f21-bad6-1a15baedb27f



## 📌 Overview

**Medical RAG Assistant** is an AI-powered question-answering system that combines **Retrieval-Augmented Generation (RAG)** with the **Gemini API** to answer questions about patient medical records.

Instead of asking a Large Language Model to generate answers from its internal knowledge, the system first retrieves relevant information from a medical knowledge base and then provides this information as context to the language model.

The system follows the pipeline:

```text
User Question
      │
      ▼
Intent Detection
      │
      ▼
Semantic Retrieval
      │
      ▼
FAISS Vector Search
      │
      ▼
Top 15 Relevant Chunks
      │
      ▼
CrossEncoder Re-ranking
      │
      ▼
Top 5 Relevant Chunks
      │
      ▼
Context + User Question
      │
      ▼
Gemini API
      │
      ▼
Medical Answer
```

## The application provides a simple conversational interface using **Streamlit**, allowing users to interact with the medical knowledge base in real time.

# 🎯 Project Objectives

The main objectives of this project are to:

* Build a practical **Retrieval-Augmented Generation** system.
* Retrieve relevant information from structured medical records and PDF reports.
* Use semantic embeddings to improve information retrieval.
* Improve retrieved results using a **CrossEncoder re-ranking stage**.
* Generate answers using the **Gemini API**.
* Restrict generated answers to the retrieved medical context.
* Provide an interactive conversational interface with Streamlit.
* Demonstrate how RAG can be applied to domain-specific knowledge.

---

# 🧠 What is RAG?

**Retrieval-Augmented Generation (RAG)** is an architecture that combines information retrieval with a generative language model.

A traditional LLM generates an answer based primarily on what it learned during training.

A RAG system follows a different approach:

```text
Question
   ↓
Search Knowledge Base
   ↓
Retrieve Relevant Information
   ↓
Build Context
   ↓
Send Context to LLM
   ↓
Generate Answer
```

This approach allows the language model to generate responses based on an external knowledge source.

In this project, the external knowledge source consists of **synthetic patient records and PDF medical reports**.

---

# 🗂️ Knowledge Base

The project uses a **synthetic medical dataset** rather than real patient data.

The dataset contains:

### `patients.json`

Structured patient information including:

* Patient ID
* First name
* Last name
* Age
* Blood type
* Marital status
* Disease
* Medication

### PDF Medical Reports

Some patients also have generated PDF reports containing laboratory information such as:

* Blood sugar
* Hemoglobin
* Cholesterol
* Diagnosis
* Medication
* Patient information

The dataset generation script creates **200 synthetic patients** with randomly generated information.

Some patients are also randomly assigned PDF reports.

---

# 🏗️ System Architecture

The complete architecture consists of several stages.

## 1. Data Preparation

The `create_data.py` script generates the synthetic medical knowledge base.

```text
create_data.py
      │
      ├── patients.json
      │
      └── PDF Reports
```

The generated patient data includes several diseases:

* Diabetes
* Hypertension
* Anemia
* Asthma
* Healthy

The script also defines a medication associated with each disease.

---

# 2. Document Construction

For each patient, the system creates a textual patient profile containing information such as:

```text
Patient Profile:
Name: ...
ID: ...
Age: ...
Disease: ...
Medication: ...
```

The system then checks whether a PDF medical report exists for that patient.

If a PDF exists, its pages are processed using `pypdf` and the extracted text is added to the knowledge base.

---

# 3. Text Embeddings

The textual medical information is converted into numerical vector representations using:

```text
all-MiniLM-L6-v2
```

This model is provided through **SentenceTransformers**.

The purpose of embeddings is to represent text in a vector space where semantically similar pieces of information are located close to each other.

For example:

```text
"What is the patient's disease?"
```

can be matched with a document containing:

```text
Disease: Diabetes
```

even though the wording is different.

The project uses `SentenceTransformer` to encode the medical text into embeddings.

---

# 4. FAISS Vector Database

The generated embeddings are stored in a **FAISS** index.

The project uses:

```python
faiss.IndexFlatL2
```

FAISS performs vector similarity search between:

```text
User Question
        ↓
Question Embedding
        ↓
FAISS Search
        ↓
Most Similar Documents
```

## For each question, the system initially retrieves the **top 15 most similar document chunks**.

# 5. Re-ranking with CrossEncoder

Retrieving documents using embeddings alone may return several potentially relevant results.

To improve the ranking, the project uses a **CrossEncoder**:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The retrieval process therefore consists of two stages:

```text
                User Question
                     │
                     ▼
              FAISS Vector Search
                     │
                     ▼
              Top 15 Candidates
                     │
                     ▼
              CrossEncoder
                Re-ranking
                     │
                     ▼
              Top 5 Results
```

The CrossEncoder evaluates the relationship between the user's question and each retrieved document.

The five highest-ranked results are then combined to form the final context.

---

# 6. Context Construction

After re-ranking, the top five relevant chunks are concatenated:

```text
Retrieved Chunk 1
       +
Retrieved Chunk 2
       +
Retrieved Chunk 3
       +
Retrieved Chunk 4
       +
Retrieved Chunk 5
       ↓
Final Context
```

This context is then provided to Gemini along with the user's question.

---

# 7. Gemini API

The project uses the **Gemini API** as the generative language model.

The configured model is:

```text
gemini-3-flash-preview
```

The model receives:

1. System instructions
2. Retrieved medical context
3. User question

The prompt explicitly instructs the model to use **only the provided context**.

If the required information cannot be found in the retrieved records, the system instructs the model to respond:

```text
The information is not available in the medical records.
```

This design helps reduce unsupported answers and keeps the generated response grounded in the retrieved knowledge base.

---

# 💬 8. Intent Detection

Before running the complete RAG pipeline, the application performs a simple intent detection step.

The system recognizes:

| Intent        | Example                |
| ------------- | ---------------------- |
| Greeting      | `hello`, `hi`, `مرحبا` |
| Goodbye       | `bye`, `مع السلامة`    |
| Thanks        | `thanks`, `شكرا`       |
| Medical Query | Any other question     |

For simple conversational messages, predefined responses are returned without executing the full retrieval pipeline.

This avoids unnecessary retrieval and LLM calls for simple interactions.

---

# 🖥️ 9. User Interface

The application interface is built using **Streamlit**.

Users can enter questions through a chat interface:

```text
┌──────────────────────────────────────────┐
│          🩺 Medical AI Assistant         │
├──────────────────────────────────────────┤
│                                          │
│ User: What disease does patient 25 have? │
│                                          │
│ AI: Patient 25 has ...                   │
│                                          │
├──────────────────────────────────────────┤
│ Ask about patients or lab results...     │
└──────────────────────────────────────────┘
```

The application displays the conversation using Streamlit's chat components.

---

# 🧠 10. Chat History

The application uses:

```python
st.session_state.messages
```

to keep previous messages visible during the current Streamlit session.

This allows users to see the conversation history while interacting with the application.

> **Important:** The current implementation keeps the conversation history visible in the interface, but previous messages are not explicitly included in the Gemini prompt for subsequent queries. Therefore, this should not be considered full multi-turn conversational memory.

---

# 🛠️ Technologies

The project is built using:

| Technology              | Purpose                   |
| ----------------------- | ------------------------- |
| 🐍 Python               | Main programming language |
| 🤖 Gemini API           | Response generation       |
| 🧠 SentenceTransformers | Text embeddings           |
| 🔎 FAISS                | Vector similarity search  |
| 🔄 CrossEncoder         | Document re-ranking       |
| 📄 pypdf                | PDF text extraction       |
| 🌐 Streamlit            | Web interface             |
| 🔢 NumPy                | Numerical processing      |
| 📑 ReportLab            | Synthetic PDF generation  |

These technologies correspond to the implementation and technical documentation of the project.

---

# 🔎 Example RAG Workflow

Suppose the user asks:

```text
What medication is patient 25 taking?
```

The system performs:

### Step 1 — User Query

```text
What medication is patient 25 taking?
```

### Step 2 — Embedding

The question is converted into a vector using:

```text
all-MiniLM-L6-v2
```

### Step 3 — Retrieval

FAISS retrieves the 15 most similar chunks.

### Step 4 — Re-ranking

The CrossEncoder scores the retrieved question-document pairs.

### Step 5 — Context Selection

The five highest-ranked chunks are selected.

### Step 6 — Generation

Gemini receives:

```text
Instructions
+
Retrieved Context
+
User Question
```

### Step 7 — Final Answer

The model generates an answer grounded in the retrieved medical records.

---

# 🔐 Grounded Generation

One of the important design decisions in this project is to constrain the language model using retrieved context.

The system prompt contains the instruction:

```text
Use ONLY the information from the provided context.
```

If the requested information is unavailable, the assistant is instructed to explicitly state that the information is not available in the medical records.

This is an important RAG principle:

```text
Knowledge Base
      ↓
Relevant Evidence
      ↓
LLM Context
      ↓
Grounded Response
```

---

# 📈 Advantages of the Approach

## Semantic Search

The system does not depend only on exact keyword matching.

Embeddings allow semantically related questions and documents to be compared in vector space.

## Re-ranking

The CrossEncoder provides an additional relevance-ranking stage after the initial FAISS retrieval.

## Grounded Answers

The language model is instructed to rely only on retrieved information.

## Multiple Data Sources

The knowledge base combines:

* Structured JSON patient profiles
* PDF medical reports

## Interactive Interface

Streamlit provides a simple chat-based interface for interacting with the system.

---

# ⚠️ Limitations

The current implementation has several limitations.

### Synthetic Data

The system uses generated medical records rather than real clinical data.

Therefore, it should be considered a **technical demonstration**, not a clinically validated system.

### Simple Chunking

PDF content is currently processed essentially at the page level rather than using a sophisticated document chunking strategy.

### Vector Search Only

The current retrieval implementation uses FAISS semantic similarity followed by CrossEncoder re-ranking.

It does not currently implement a hybrid retrieval strategy such as:

```text
BM25 + Embeddings
```

### Limited Conversational Memory

Conversation history is maintained in Streamlit so that previous messages remain visible, but the previous conversation is not explicitly passed to Gemini when generating a new response.

### Dataset Size

The synthetic dataset contains only 200 generated patient records, which is relatively small for evaluating a production-scale retrieval system.

These limitations are consistent with the project's documented future improvements.

---

# 🚀 Future Improvements

Several improvements can make the system more powerful and reliable.

## 1. Hybrid Search

Combine:

```text
BM25
+
Dense Vector Search
```

to benefit from both keyword-based and semantic retrieval.

## 2. Better Document Chunking

Instead of treating PDF pages as the main text units, implement intelligent chunking based on:

* Sections
* Medical concepts
* Paragraphs
* Tables
* Report structure

## 3. Larger Knowledge Base

Expand the number and diversity of medical documents.

## 4. Multi-Turn Conversation

Pass relevant previous conversation history to the language model so that users can ask follow-up questions naturally.

## 5. Improved Metadata Filtering

Use patient IDs and document metadata to restrict retrieval to the relevant patient before semantic search.

## 6. Better Evaluation

Introduce a dedicated RAG evaluation framework measuring:

* Retrieval precision
* Retrieval recall
* Context relevance
* Answer faithfulness
* Answer correctness

---

# 🧪 Educational Purpose

This project demonstrates the integration of several modern AI concepts:

```text
LLM
 │
 ├── Retrieval-Augmented Generation
 │
 ├── Semantic Embeddings
 │
 ├── Vector Databases
 │
 ├── Re-ranking
 │
 ├── Prompt Engineering
 │
 └── Conversational UI
```

It is intended as an **educational and research project** demonstrating how RAG can be applied to a domain-specific knowledge base.

---

# ⚠️ Medical Disclaimer

This project is intended **for educational and research purposes only**.

It does not constitute a medical diagnostic system and should not be used to:

* Diagnose diseases
* Recommend treatments
* Replace healthcare professionals
* Make clinical decisions

The dataset used by this project is synthetic and does not represent real patient records.

---

# 👩‍💻 Author

**Chaima Mansouri**

AI & Deep Learning
Computer Vision • Generative AI • RAG Systems

---

# 📚 Documentation

A technical documentation file is included with the project and describes:

* System architecture
* Dataset
* Embeddings
* FAISS retrieval
* CrossEncoder re-ranking
* Gemini generation
* Streamlit interface
* Future improvements

---

# ⭐ Acknowledgments

This project was developed as a practical exploration of:

* Retrieval-Augmented Generation
* Large Language Models
* Vector Search
* Semantic Retrieval
* Medical AI applications
* Generative AI

Special thanks to the open-source communities behind **SentenceTransformers, FAISS, Streamlit, PyPDF, NumPy, and ReportLab**.

---

# 📜 License

This project is intended for educational and research purposes.

Please review the licenses and terms of use of the external models, APIs, libraries, and datasets before using this project in a production environment.


