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

### 🛠️ Setup Instructions

#### 1. Clone the Repository

```bash
git clone <https://github.com/IMMORTALWOL/ai-claims-adjudicator>
cd <ai-claims-adjudicator>
```

#### 2. Set Up the Environment

Create and activate a virtual environment:

```bash
# Create the environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

#### 3. Add Policy Documents

Create a folder named `policy_documents` in the root of the project directory and place your insurance policy PDF files inside it:

```bash
mkdir policy_documents
```

#### 4. Run the Application

Launch the Streamlit app from your terminal:

```bash
streamlit run app.py
```

#### 5. Using the App

- The app will open in your web browser.
- In the sidebar, enter your **Gemini API Key**.
- Click the **"Scan for New Documents & Update Index"** button.  
  The app will process the PDFs in the `policy_documents` folder.  
  *(This only needs to be done once per new document.)*
- Once the index is ready, enter a claim detail in the main text area and click **"Process New Claim"**.
- Follow the conversational prompts if the AI needs more information.

---

## 🔮 Future Enhancements

- **Support for More Document Types:**  
  Extend the document loader to handle `.docx`, `.txt`, and `.html` files.

- **Hybrid Search:**  
  Combine the current semantic search with traditional keyword search (e.g., BM25) to improve retrieval accuracy for queries containing specific codes or jargon.

- **Database Integration:**  
  Store claim results and conversation history in a database (like SQLite or PostgreSQL) for long-term auditing and analysis.

- **Advanced UI:**  
  Display retrieved clauses, scores, and structured claim data in a visual format.

---

## 🤝 Contributing

Pull requests and feedback are welcome! If you’d like to contribute, fork the repo and submit a PR with your enhancements.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## ✉️ Contact

Built by [Your Name]  
For questions or support, contact: [your-email@example.com]
