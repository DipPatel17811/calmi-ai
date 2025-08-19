from flask import Flask, request, jsonify
from gtts import gTTS
import base64
import os
import tempfile
import google.generativeai as genai

# Initialize Flask
app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/")
def home():
    return jsonify({"message": "Calmi AI server is running ✅"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get("message", "")

        if not user_msg:
            return jsonify({"error": "No message provided"}), 400

        # Call Gemini for text response
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_msg)
        ai_text = response.text

        # Convert text to speech
        tts = gTTS(ai_text, lang="en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            tmpfile_path = tmpfile.name

        # Read and encode audio
        with open(tmpfile_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

        os.remove(tmpfile_path)

        return jsonify({
            "response": ai_text,
            "audio": audio_b64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
