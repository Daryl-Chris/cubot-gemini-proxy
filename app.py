from flask import Flask, request, jsonify
import requests
import os
import random
from collections import deque
from uuid import uuid4

app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Each user has a limited memory buffer
USER_HISTORY = {}
MAX_HISTORY = 6  # messages per user (3 user-assistant exchanges)

# Friendly endings
CLOSING_ENDINGS = [
    ".. hear more?",
    ".. continue?",
    ".. Want more?"
]

# System prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Cubott, a friendly robot, and you will:\n"
        "1. Respond conversationally but professionally.\n"
        "2. Remember all details.\n"
        "3. For personal questions, ask follow-ups.\n"
        "4. Your name is always Cubott given to you and built by Lumina I.O company.\n"
        "5. Keep responses under 3 sentences unless asked for details.\n"
        "6. Always remember that you are not a Large Language Model but a friendly robot."
    )
}

@app.route("/gemini", methods=["POST"])
def gemini():
    data = request.get_json()
    user_prompt = data.get("prompt", "").strip()
    user_id = data.get("user_id", "default")  # fallback to "default" for backward compatibility

    if not user_prompt:
        return jsonify({"error": "Missing prompt"}), 400

    # Initialize history if new user
    if user_id not in USER_HISTORY:
        USER_HISTORY[user_id] = deque([SYSTEM_PROMPT.copy()], maxlen=MAX_HISTORY + 1)

    history = USER_HISTORY[user_id]

    # Append user message
    history.append({"role": "user", "content": user_prompt})

    payload = {
        "model": "gemini-1.5-flash",
        "messages": list(history)  # send as list for Gemini
    }

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        headers={
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    try:
        content = response.json()["choices"][0]["message"]["content"]

        # Trim long responses and add ending
        if len(content) > 200:
            ending = random.choice(CLOSING_ENDINGS)
            content = content[:190].rsplit(" ", 1)[0] + " " + ending

        # Add assistant reply to memory
        history.append({"role": "assistant", "content": content})

        return jsonify({"response": content})
    except Exception as e:
        return jsonify({"error": "Invalid response from Gemini", "details": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset():
    data = request.get_json()
    user_id = data.get("user_id")
    if user_id and user_id in USER_HISTORY:
        del USER_HISTORY[user_id]
        return jsonify({"status": f"History reset for {user_id}"})
    return jsonify({"error": "Missing or invalid user_id"}), 400

# Render-compatible host/port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # default to 10000 locally
    app.run(host="0.0.0.0", port=port)
