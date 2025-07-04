from flask import Flask, request, jsonify
import requests
import os
import random

app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# List of friendly endings
CLOSING_ENDINGS = [
    "... Let me know if you'd like to hear more.",
    "... Would you like me to continue?",
    "... Just say the word if you want more!"
]

@app.route("/gemini", methods=["POST"])
def gemini():
    user_prompt = request.json.get("prompt", "")
    if not user_prompt:
        return jsonify({"error": "Missing prompt"}), 400

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        headers={
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gemini-1.5-flash",
            "messages": [
                {"role": "system", "content": "You are Cubot, a friendly robot assistant."},
                {"role": "user", "content": user_prompt}
            ]
        }
    )

    try:
        content = response.json()["choices"][0]["message"]["content"]

        # Trim and append a random closing if content is too long
        if len(content) > 200:
            ending = random.choice(CLOSING_ENDINGS)
            content = content[:190].rsplit(" ", 1)[0] + " " + ending

        return jsonify({"response": content})
    except:
        return jsonify({"error": "Invalid response from Gemini"}), 500

# ✅ This line tells Render to listen on port 10000 publicly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
