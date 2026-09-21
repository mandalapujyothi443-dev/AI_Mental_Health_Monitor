from flask import Blueprint, jsonify, render_template, request, session
from utils.security import login_required
from services.assistant_service import chat_response, transcribe_audio

assistant_bp = Blueprint("assistant", __name__, url_prefix="/assistant")

@assistant_bp.get("/")
@login_required
def page():
    return render_template("assistant.html")

@assistant_bp.post("/chat")
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []
    if not message:
        return jsonify({"error": "Message is required."}), 400

    try:
        answer = chat_response(message, history)
        return jsonify({"answer": answer})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@assistant_bp.post("/transcribe")
@login_required
def transcribe():
    audio = request.files.get("audio")
    language = (request.form.get("language") or "").strip() or None
    if not audio:
        return jsonify({"error": "No audio file received."}), 400

    try:
        text = transcribe_audio(audio, language)
        return jsonify({"text": text})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
