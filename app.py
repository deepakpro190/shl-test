'''from flask import Flask, request, render_template
from utils.faiss_utils import store_results_to_faiss, query_faiss
from agents.query_analysis import analyze_query_with_mistral
from utils.response_generator import generate_response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import subprocess
import shutil
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Install Chrome if it's not available
def install_chrome_if_missing():
    if shutil.which("google-chrome") is None:
        print("Chrome not found, installing...")
        try:
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(["apt-get", "install", "-y", "wget", "gnupg", "unzip"], check=True)
            subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"], check=True)
            subprocess.run(["apt", "install", "-y", "./google-chrome-stable_current_amd64.deb"], check=True)
        except Exception as e:
            print("Failed to install Chrome:", e)

# Set up headless Chrome driver
def get_chrome_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    user_query = ""
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

                # Ensure Chrome is ready before calling any script that may use it
                #install_chrome_if_missing()

                if analysis["keywords"]:
                    print(f" Running first.py with keywords: {analysis['keywords']}")
                    subprocess.run(["python", "scripts/first.py", *analysis["keywords"]], check=True)

                if any([analysis["job_family"], analysis["job_level"], analysis["industry"], analysis["language"]]):
                    print(" Running second.py with job details...")
                    subprocess.run([
                        "python", "scripts/second.py",
                        "--family", analysis["job_family"],
                        "--level", analysis["job_level"],
                        "--industry", analysis["industry"],
                        "--language", analysis["language"]
                    ], check=True)

                if analysis["job_category"]:
                    print(" Running third.py with category...")
                    subprocess.run([
                        "python", "scripts/third.py",
                        "--category", analysis["job_category"]
                    ], check=True)

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
    else:
        print(f"Method is: {request.method}")

        print("SOMETHING HAPPENDED , DONT KNOW")

    return render_template("index.html", response=response, user_query=user_query)
'''
@app.route("/process_query", methods=["POST"])
def process_query():
    try:
        user_query = request.form.get("user_query", "").strip()
        print(f"Received query: {user_query}")
        
        # Add back query analysis
        try:
            from agents.query_analysis import analyze_query_with_mistral
            analysis = analyze_query_with_mistral(user_query)
            
            # Add back script execution
            import subprocess
            
            # Run first script if keywords exist
            if analysis.get("keywords"):
                print(f"Running first.py with keywords: {analysis['keywords']}")
                subprocess.run(["python", "scripts/first.py", *analysis["keywords"]], 
                              check=False, timeout=60)
            
            return jsonify({
                "success": True,
                "response": f"Analysis and first script complete"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "response": f"Processing failed: {str(e)}"
            })
        
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": False, 
            "response": f"Error: {str(e)}"
        })
