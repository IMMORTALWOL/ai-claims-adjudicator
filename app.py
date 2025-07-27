import streamlit as st
import json
import os
from utils import (
    get_embedding_model,
    update_vector_store,
    load_vector_store,
    search_relevant_clauses,
    call_gemini_api,
    get_structured_decision,
    DOCS_DIR
)
from prompts import (
    QUERY_STRUCTURING_PROMPT, 
    DECISION_MAKING_PROMPT, 
    FINAL_SUMMARY_PROMPT,
    FOLLOW_UP_DECISION_PROMPT
)

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="AI Insurance Claims Adjudicator",
    page_icon="⚖️",
    layout="wide"
)

# --- State Management ---
# Initialize all session state variables at the top
default_values = {
    'index_ready': False,
    'index': None,
    'chunks': None,
    'processed_files': [],
    'gemini_api_key': "",
    'conversation_history': []
}
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Main App Logic ---
model = get_embedding_model()

# Try to load the existing vector store on startup
if not st.session_state.index_ready:
    index, chunks, processed_files = load_vector_store()
    if index is not None:
        st.session_state.update({
            'index': index,
            'chunks': chunks,
            'processed_files': processed_files,
            'index_ready': True
        })

# --- UI Layout ---
st.title("⚖️ AI-Powered Insurance Claims Adjudicator")

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")
    st.session_state.gemini_api_key = st.text_input(
        "Enter your Gemini API Key", type="password",
        value=st.session_state.gemini_api_key
    )
    st.markdown("---")
    st.header("Knowledge Base Management")
    st.info(f"Place policy PDFs in: `{DOCS_DIR}`")
    if st.button("Scan for New Documents & Update Index"):
        if model:
            with st.spinner("Updating index..."):
                index, chunks, processed_files = update_vector_store(model)
                st.session_state.update({
                    'index': index, 'chunks': chunks,
                    'processed_files': processed_files,
                    'index_ready': index is not None
                })
                if st.session_state.index_ready:
                    st.success("Index updated!")
    st.markdown("---")
    st.subheader("Indexed Documents:")
    st.write(st.session_state.processed_files or "None")

# --- Main Panel ---
st.header("Process a Claim")

if st.session_state.index_ready:
    st.success(f"Knowledge base is ready.")
    
    initial_query = st.text_area(
        "Enter the initial claim details:",
        "46-year-old male, knee surgery in Pune, 3-month-old insurance policy",
        height=100, key="initial_query"
    )

    if st.button("Process New Claim", key="process_new"):
        st.session_state.conversation_history = [] # Reset for a new claim
        if not st.session_state.gemini_api_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
        elif initial_query and model:
            with st.spinner("Processing..."):
                structuring_prompt = QUERY_STRUCTURING_PROMPT.format(query=initial_query)
                structured_query_str = call_gemini_api(structuring_prompt, st.session_state.gemini_api_key)
                if not structured_query_str:
                    st.error("Could not structure the query.")
                else:
                    try:
                        clean_str = structured_query_str.strip().replace("```json", "").replace("```", "").strip()
                        structured_query = json.loads(clean_str)
                        
                        relevant_clauses = search_relevant_clauses(
                            initial_query, model, st.session_state.index, st.session_state.chunks
                        )
                        
                        clauses_text = "\n\n---\n\n".join([f"Clause from {c['metadata']['source']}, Page {c['metadata']['page']}:\n{c['text']}" for c in relevant_clauses])
                        
                        # --- CORRECTED FUNCTION CALL ---
                        decision_json = get_structured_decision(
                            DECISION_MAKING_PROMPT,
                            st.session_state.gemini_api_key,
                            structured_query=json.dumps(structured_query, indent=2),
                            clauses=clauses_text
                        )
                        
                        st.session_state.conversation_history.append({
                            "structured_query": structured_query,
                            "relevant_clauses": relevant_clauses,
                            "decision_json": decision_json
                        })
                    except json.JSONDecodeError:
                        st.error("Failed to parse the structured query from the LLM.")
                        st.text_area("Raw LLM Response", structured_query_str)

# --- Display Conversation History and Handle Follow-ups ---
if st.session_state.conversation_history:
    st.markdown("---")
    st.subheader("Adjudication Conversation")
    
    for i, turn in enumerate(st.session_state.conversation_history):
        st.markdown(f"**Turn {i+1}**")
        decision = turn['decision_json']
        
        summary_prompt = FINAL_SUMMARY_PROMPT.format(decision_json=json.dumps(decision))
        simple_summary = call_gemini_api(summary_prompt, st.session_state.gemini_api_key)
        if simple_summary:
            st.markdown(f"> {simple_summary}")
        
        with st.expander("Show Detailed Breakdown"):
            st.write("**Structured Details:**"); st.json(turn['structured_query'])
            st.write("**Retrieved Clauses:**")
            for clause in turn['relevant_clauses']:
                st.info(f"**From {clause['metadata']['source']}, Page {clause['metadata']['page']}:**\n\n{clause['text']}")
            st.write("**Detailed Adjudication:**"); st.json(decision)

    last_decision = st.session_state.conversation_history[-1]['decision_json']
    if last_decision and last_decision.get("decision") == "Needs More Information":
        st.info("The AI needs more information. Please provide the details below.")
        
        follow_up_query = st.text_area("Provide the requested information here:", height=100, key="follow_up")

        if st.button("Submit Additional Information", key="submit_follow_up"):
            if follow_up_query:
                with st.spinner("Re-evaluating claim..."):
                    last_turn = st.session_state.conversation_history[-1]
                    clauses_text = "\n\n---\n\n".join([f"Clause from {c['metadata']['source']}, Page {c['metadata']['page']}:\n{c['text']}" for c in last_turn['relevant_clauses']])
                    
                    # --- CORRECTED FUNCTION CALL FOR FOLLOW-UP ---
                    new_decision_json = get_structured_decision(
                        FOLLOW_UP_DECISION_PROMPT,
                        st.session_state.gemini_api_key,
                        structured_query=json.dumps(last_turn['structured_query'], indent=2),
                        clauses=clauses_text,
                        previous_justification=json.dumps(last_turn['decision_json']['justification'], indent=2),
                        user_follow_up=follow_up_query
                    )

                    st.session_state.conversation_history.append({
                        "structured_query": last_turn['structured_query'],
                        "relevant_clauses": last_turn['relevant_clauses'],
                        "decision_json": new_decision_json
                    })
                    st.rerun()

else:
    if st.session_state.index_ready:
        st.info("Enter claim details and click 'Process New Claim' to start.")
    else:
        st.warning("Knowledge base not ready. Add PDFs to the `policy_documents` folder and update index via sidebar.")

