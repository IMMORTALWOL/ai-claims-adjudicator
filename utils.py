import streamlit as st
import os
import pickle
import numpy as np
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import requests
import json

# --- CONFIGURATION ---
MODEL_NAME = 'all-MiniLM-L6-v2'
VECTOR_STORE_PATH = "vector_store.pkl"
DOCS_DIR = "policy_documents"

# --- CORE FUNCTIONS ---

@st.cache_resource
def get_embedding_model():
    """Loads and caches the SentenceTransformer model."""
    st.write("Loading embedding model for the session...")
    try:
        model = SentenceTransformer(MODEL_NAME)
        return model
    except Exception as e:
        st.error(f"Error loading sentence transformer model: {e}")
        return None

def extract_text_from_pdf_paths(pdf_paths):
    """Extracts text from a list of PDF file paths."""
    documents = []
    for pdf_path in pdf_paths:
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                file_name = os.path.basename(pdf_path)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text:
                        documents.append({
                            "text": text,
                            "metadata": {"source": file_name, "page": page_num + 1}
                        })
        except Exception as e:
            st.warning(f"Could not read {pdf_path}: {e}")
    return documents

def chunk_text(documents, chunk_size=1000, chunk_overlap=200):
    """Splits documents into smaller, overlapping chunks."""
    chunks = []
    for doc in documents:
        text = doc["text"]
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk_text = text[i:i + chunk_size]
            chunks.append({
                "text": chunk_text,
                "metadata": doc["metadata"]
            })
    return chunks

def update_vector_store(model):
    """Scans the DOCS_DIR, processes new PDFs, and updates the vector store."""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        st.info(f"Created a directory for your documents: '{DOCS_DIR}'. Please add your policy PDFs there.")
        return None, [], []

    if os.path.exists(VECTOR_STORE_PATH):
        with open(VECTOR_STORE_PATH, "rb") as f:
            vector_store = pickle.load(f)
            index = faiss.deserialize_index(vector_store["index"])
            all_chunks = vector_store["chunks"]
            processed_files = vector_store.get("processed_files", [])
    else:
        index = None
        all_chunks = []
        processed_files = []

    pdf_files_in_dir = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]
    new_files_to_process = [f for f in pdf_files_in_dir if f not in processed_files]

    if not new_files_to_process:
        st.write("No new documents to process. Index is up-to-date.")
        return index, all_chunks, processed_files

    st.write(f"Found {len(new_files_to_process)} new document(s) to process: {', '.join(new_files_to_process)}")
    
    new_pdf_paths = [os.path.join(DOCS_DIR, f) for f in new_files_to_process]
    new_documents = extract_text_from_pdf_paths(new_pdf_paths)
    new_chunks = chunk_text(new_documents)
    
    if not new_chunks:
        st.warning("Could not extract any text from the new documents.")
        return index, all_chunks, processed_files

    new_embeddings = model.encode([chunk['text'] for chunk in new_chunks], show_progress_bar=True)
    
    if index is None:
        dimension = new_embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
    
    index.add(np.array(new_embeddings, dtype=np.float32))
    all_chunks.extend(new_chunks)
    processed_files.extend(new_files_to_process)

    updated_vector_store = {
        "index": faiss.serialize_index(index),
        "chunks": all_chunks,
        "processed_files": processed_files
    }
    with open(VECTOR_STORE_PATH, "wb") as f:
        pickle.dump(updated_vector_store, f)
    
    st.success(f"Successfully updated index with {len(new_chunks)} new text chunks.")
    return index, all_chunks, processed_files


def load_vector_store():
    """Loads a FAISS vector store from disk."""
    if os.path.exists(VECTOR_STORE_PATH):
        with open(VECTOR_STORE_PATH, "rb") as f:
            vector_store = pickle.load(f)
            index = faiss.deserialize_index(vector_store["index"])
            processed_files = vector_store.get("processed_files", [])
            return index, vector_store["chunks"], processed_files
    return None, [], []

def search_relevant_clauses(query, model, index, chunks, top_k=5):
    """Performs semantic search to find relevant clauses."""
    if index is None:
        return []
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding, dtype=np.float32), top_k)
    
    relevant_chunks = [chunks[i] for i in indices[0]]
    return relevant_chunks

def call_gemini_api(prompt, api_key):
    """A generic function to call the Gemini API with a provided API key."""
    if not api_key:
        st.error("Gemini API Key is missing. Please provide it in the sidebar.")
        return None
        
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.error(f"Gemini API returned no candidates. Response: {result}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Gemini API: {e}")
        st.error(f"Response Body: {response.text if 'response' in locals() else 'No response'}")
        return None
    except (KeyError, IndexError) as e:
        st.error(f"Unexpected API response structure. Error: {e}. Response: {result}")
        return None

def get_structured_decision(decision_prompt_template, api_key, **kwargs):
    """
    Gets the final decision from the LLM by formatting the provided template
    with the given keyword arguments.
    """
    prompt = decision_prompt_template.format(**kwargs)
    
    response_text = call_gemini_api(prompt, api_key)
    if response_text:
        try:
            clean_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except json.JSONDecodeError as e:
            st.error(f"Failed to decode JSON response from LLM. Error: {e}")
            st.text_area("Raw LLM Response", response_text, height=200)
            return None
    return None
