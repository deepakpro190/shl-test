'''import streamlit as st
from utils.faiss_utils import store_results_to_faiss, query_faiss

from agents.query_analysis import analyze_query_with_mistral
from utils.response_generator import generate_response
import os
import subprocess

os.system('playwright install')
os.system('playwright install-deps')
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
'''
from flask import Flask, request, render_template
from utils.faiss_utils import store_results_to_faiss, query_faiss
from agents.query_analysis import analyze_query_with_mistral
from utils.response_generator import generate_response
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load API key from .env
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    user_query=""
    print("HELOO WORLD")
    if request.method == "POST":
        try:
            print(" Received POST request")
            user_query = request.form.get("user_query", "").strip()
            print(f" User query: {user_query}")

            if user_query:
                print(" Analyzing query...")
                analysis = analyze_query_with_mistral(user_query)
                print(f" Analysis result: {analysis}")

                if analysis["keywords"]:
                    print(f" Running first.py with keywords: {analysis['keywords']}")
                    os.system(f"python scripts/first.py {' '.join(analysis['keywords'])}")

                if any([analysis["job_family"], analysis["job_level"], analysis["industry"], analysis["language"]]):
                    print(" Running second.py with job details...")
                    os.system(f"python scripts/second.py --family '{analysis['job_family']}' --level '{analysis['job_level']}' --industry '{analysis['industry']}' --language '{analysis['language']}'")

                if analysis["job_category"]:
                    print(" Running third.py with category...")
                    os.system(f"python scripts/third.py --category '{analysis['job_category']}'")

                print(" Storing results to FAISS...")
                store_results_to_faiss()

                print(" Querying FAISS...")
                results = query_faiss(user_query)
                print(f" FAISS Results: {results}")

                print(" Generating final response...")
                response = generate_response(user_query, results)
                print(" Response generated.")

        except Exception as e:
            print(" An error occurred:", e)
            response = "Oops! Something went wrong. Please try again."

    return render_template("index.html", response=response, user_query=user_query)

'''
from flask import Flask,render_template,request

app = Flask(__name__)

@app.route('/')
def run():
    return render_template('home.html')

@app.route('/submit', methods=['POST'])
def marks():
    Physics=int(request.form['Physics'])
    Maths= int(request.form['Maths'])
    Chemistry = int(request.form['Chemistry'])
    Hindi = int(request.form['Hindi'])
    English = int(request.form['English'])
    result = Physics + Maths + Chemistry + Hindi + English
    Percentage = result/5
    return render_template('home.html',Percentage=Percentage)

if __name__=='__main__':
    app.run(debug=True)
'''
