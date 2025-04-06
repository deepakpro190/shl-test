import streamlit as st
from utils.faiss_utils import init_faiss, store_results_to_faiss, query_faiss
from agents.query_analysis import analyze_query_with_mistral
from utils.response_generator import generate_response
import os

MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

st.set_page_config(page_title="🧠 SHL Assessment Recommender", layout="wide")
st.title("🧠 SHL Assessment Recommender")

# Initialize session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

# Display history
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.write(chat["bot"])

# Input UI
col1, col2 = st.columns([8, 1])
with col1:
    user_query = st.text_input("💬 Enter a job description or query:", key="query_input")

if st.button("🚀 Submit Query"):
    if user_query.strip():
        st.session_state.user_query = user_query
        st.write("🔍 Analyzing your query...")

        # ✅ Step 1: Extract intent from LLM
        analysis = analyze_query_with_mistral(user_query)

        # ✅ Step 2: Based on analysis, run crawl scripts conditionally
        if analysis["keywords"]:
            os.system(f"python scripts/first.py {' '.join(analysis['keywords'])}")

        if any([analysis["job_family"], analysis["job_level"], analysis["industry"], analysis["language"]]):
            os.system(f"python scripts/second.py --family '{analysis['job_family']}' --level '{analysis['job_level']}' --industry '{analysis['industry']}' --language '{analysis['language']}'")

        if analysis["job_category"]:
            os.system(f"python scripts/third.py --category '{analysis['job_category']}'")

        # ✅ Step 3: Store crawled CSVs to FAISS
        store_results_to_faiss()

        # ✅ Step 4: Query FAISS for results
        results = query_faiss(user_query)

        # ✅ Step 5: Use LLM to generate table response
        response = generate_response(user_query, results)

        # ✅ Save to chat history
        st.session_state.chat_history.append({"user": user_query, "bot": response})

        st.write(response)
        st.session_state.user_query = ""
