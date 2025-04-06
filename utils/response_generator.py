import requests

import os
def generate_response(user_query, results):
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

    if not results:
        return "❌ No relevant assessments found."

    context = "\n".join([f"{r[0]} (Link: {r[1]})" for r in results])

    prompt = f"""
You are a career assistant. Given the user's query: "{user_query}", recommend the 5-10 most relevant SHL assessments from the context below.
Only include:

- Assessment Name (linked)
- Remote Testing: Yes/No
- Adaptive/IRT: Yes/No
- Duration (if present)
- Test Type (if available)

Present results as a table.

Context:
{context}
"""

    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
        json={
            "model": "open-mistral-7b",
            "messages": [
                {"role": "system", "content": "You are an assistant that recommends assessments based on context."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 400,
            "temperature": 0.2,
        },
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ LLM error: {response.status_code} - {response.text}"
