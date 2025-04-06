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

