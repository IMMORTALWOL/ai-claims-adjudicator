# ⚖️ AI-Powered Insurance Claims Adjudicator

An advanced, conversational AI system designed to **automate the initial adjudication of insurance claims**. It uses a **Retrieval-Augmented Generation (RAG)** pipeline to process complex policy documents and respond intelligently to natural language queries from users or claims processors.

---

## ✨ Features

- **📚 Persistent Knowledge Base**  
  Simply place your insurance policy PDFs into the `policy_documents` folder. The system automatically processes and indexes them.

- **♻️ Incremental Updates**  
  Only new or changed documents are indexed, saving processing time.

- **💬 Natural Language Querying**  
  Users can submit claims in plain English like:  
  `46M, knee surgery, Pune, 3-month policy`

- **🧠 Multi-Step AI Reasoning Chain**
  - **Query Structuring:** Parses and converts claim into structured JSON.
  - **Semantic Retrieval:** Uses FAISS and sentence-transformers to retrieve relevant clauses.
  - **Evidence-Based Decision:** Final LLM call returns a decision with justification.
  - **Conversational Follow-ups:** Asks for more details if needed.

- **📝 Dual Output**
  - Short summary decision: `✅ Approved | ❌ Rejected | ❓ Needs More Information`
  - Detailed JSON justification including referenced clauses.

- **🖥️ Interactive Streamlit UI**
  - Web-based frontend to interact with the system easily.

---

## 🏗️ Architecture: Retrieval-Augmented Generation (RAG)

### Indexing Pipeline (Offline)
1. Load policy PDFs from `policy_documents/`
2. Chunk and embed content using `sentence-transformers`
3. Store embeddings in a FAISS index

### Inference Pipeline (Real-Time)
1. **Gemini LLM (Step 1):** Structure user query into JSON
2. **Retriever:** Semantic search using FAISS
3. **Prompt Augmentation:** Merge query + relevant policy chunks
4. **Gemini LLM (Step 2):** Adjudicate claim with context
5. **Conversation Loop:** Follow-up if more data is needed

---

## 🚀 How to Use

### 📦 Prerequisites

- Python 3.9+
- Gemini API Key from [Google AI Studio](https://makersuite.google.com/)

---


