from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
        return jsonify({"response": content})
    except:
        return jsonify({"error": "Invalid response from Gemini"}), 500
