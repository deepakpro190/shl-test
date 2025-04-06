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
from flask import Flask, request, render_template, jsonify
from utils.faiss_utils import store_results_to_faiss, query_faiss
from agents.query_analysis import analyze_query_with_mistral
from utils.response_generator import generate_response
import subprocess
import traceback
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def run_script_safely(script_path, args=None, timeout=60):
    """Run a script with proper error handling and timeout"""
    cmd = ["python", script_path]
    if args:
        if isinstance(args, list):
            cmd.extend(args)
        else:
            cmd.append(args)
    
    try:
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, timeout=timeout, 
                              capture_output=True, text=True)
        print(f"Command output: {result.stdout}")
        return True
    except subprocess.TimeoutExpired as e:
        print(f"Command timed out after {timeout} seconds: {e}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Failed to run {script_path}: {e}")
        return False

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/process_query", methods=["POST"])
def process_query():
    start_time = time.time()
    debug_info = []
    debug_info.append(f"Request method: {request.method}")
    debug_info.append(f"Request form: {request.form}")
    
    try:
        user_query = request.form.get("user_query", "").strip()
        debug_info.append(f"User query: {user_query}")
        
        if not user_query:
            return jsonify({"success": False, "response": "No query provided"})
        
        # Analyze the query
        debug_info.append("Analyzing query...")
        try:
            analysis = analyze_query_with_mistral(user_query)
            debug_info.append(f"Analysis result: {analysis}")
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            debug_info.append(error_msg)
            return jsonify({"success": False, "response": error_msg})
        
        # Process keywords
        if analysis.get("keywords"):
            debug_info.append(f"Running first.py with keywords: {analysis['keywords']}")
            run_script_safely("scripts/first.py", analysis["keywords"])
        
        # Process job details
        job_params = {
            "--family": analysis.get("job_family", ""),
            "--level": analysis.get("job_level", ""),
            "--industry": analysis.get("industry", ""),
            "--language": analysis.get("language", "")
        }
        
        if any(val for val in job_params.values()):
            args = []
            for key, value in job_params.items():
                if value:
                    args.extend([key, value])
            debug_info.append(f"Running second.py with args: {args}")
            run_script_safely("scripts/second.py", args)
        
        # Process job category
        if analysis.get("job_category"):
            debug_info.append(f"Running third.py with category: {analysis['job_category']}")
            run_script_safely("scripts/third.py", ["--category", analysis["job_category"]])
        
        # Store results in FAISS
        debug_info.append("Storing results to FAISS...")
        try:
            store_results_to_faiss()
        except Exception as e:
            error_msg = f"FAISS storage failed: {str(e)}"
            debug_info.append(error_msg)
            return jsonify({"success": False, "response": error_msg})
        
        # Query FAISS
        debug_info.append("Querying FAISS...")
        try:
            results = query_faiss(user_query)
            debug_info.append(f"FAISS results count: {len(results) if results else 0}")
        except Exception as e:
            error_msg = f"FAISS query failed: {str(e)}"
            debug_info.append(error_msg)
            return jsonify({"success": False, "response": error_msg})
        
        # Generate response
        debug_info.append("Generating response...")
        try:
            response = generate_response(user_query, results)
            debug_info.append("Response generated successfully")
        except Exception as e:
            error_msg = f"Response generation failed: {str(e)}"
            debug_info.append(error_msg)
            return jsonify({"success": False, "response": error_msg})
        
        elapsed_time = time.time() - start_time
        debug_info.append(f"Total processing time: {elapsed_time:.2f} seconds")
        
        # Print all debug info to console
        for line in debug_info:
            print(line)
        
        return jsonify({
            "success": True,
            "response": response,
            "processing_time": f"{elapsed_time:.2f} seconds"
        })
        
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({
            "success": False, 
            "response": "An error occurred while processing your request."
        })

