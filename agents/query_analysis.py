def analyze_query_with_mistral(query):
    import json
    import re
    import os

    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    system_prompt = """
You are an assistant that extracts job-related attributes from user queries to choose which script to run.
Return a JSON with the following fields:
- keywords (list of strings)
- job_family (string or null)
- job_level (string or null)
- industry (string or null)
- language (string or null)
- job_category (string or null)
"""

    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
            json={
                "model": "open-mistral-7b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 300,
                "temperature": 0.3,
            },
        )

        # Debug print
        print("Mistral raw response:", response.text)

        res_json = response.json()

        if "choices" not in res_json:
            raise ValueError("Missing 'choices' in response")

        result = res_json["choices"][0]["message"]["content"]
        return json.loads(result)

    except Exception as e:
        print(f"[ERROR] Fallback used. Reason: {e}")
        return {
            "keywords": re.findall(r"\b\w+\b", query),
            "job_family": None,
            "job_level": None,
            "industry": None,
            "language": None,
            "job_category": None
        }
