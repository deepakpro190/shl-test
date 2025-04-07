
from flask import Flask, request, render_template, jsonify
import os
import subprocess
import traceback
import requests
from utils.faiss_utils import store_results_to_faiss, query_faiss
from utils.response_generator import generate_response

# Optional: Install Playwright browsers only if needed
if not os.path.exists("/opt/render/.cache/ms-playwright"):
    print("⏬ Installing Playwright browsers...")
    os.system("playwright install chromium")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/process_query", methods=["POST"])
def process_query():
    try:
        user_query = request.form.get("user_query", "").strip()
        print(f"Received query: {user_query}")

        # Step 1: Analyze query using Mistral
        from agents.query_analysis import analyze_query_with_mistral
        analysis = analyze_query_with_mistral(user_query)

        # Step 2: Run first.py if keywords are found
        if analysis.get("keywords"):
            print(f"Running first.py with keywords: {analysis['keywords']}")
            subprocess.run(
                ["python", "scripts/first.py", *analysis["keywords"]],
                check=False,
                timeout=60
            )

        # Step 3: Run second.py if job details are available
        if any([analysis.get("job_family"), analysis.get("job_level"), analysis.get("industry"), analysis.get("language")]):
            print("Running second.py with job details...")
            subprocess.run([
                "python", "scripts/second.py",
                "--family", analysis.get("job_family", ""),
                "--level", analysis.get("job_level", ""),
                "--industry", analysis.get("industry", ""),
                "--language", analysis.get("language", "")
            ], check=True)

        # Step 4: Run third.py if job category is available
        if analysis.get("job_category"):
            print("Running third.py with category...")
            subprocess.run([
                "python", "scripts/third.py",
                "--category", analysis["job_category"]
            ], check=True)

        # Step 5: Index results into FAISS
        print("Storing results to FAISS...")
        store_results_to_faiss()

        # Step 6: Query FAISS for top matches
        print("Querying FAISS...")
        results = query_faiss(user_query)
        print(f"FAISS Results: {results}")

        # Step 7: Generate final response using Mistral
        print("Generating final response...")
        response = generate_response(user_query, results)
        print("Response generated.")

        return jsonify({"success": True, "response": response})

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "response": f"Error: {str(e)}"
        })
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Fallback to 8000 locally
    app.run(host="0.0.0.0", port=port)
