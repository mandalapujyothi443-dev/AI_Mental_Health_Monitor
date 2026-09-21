import os
import tempfile
from pathlib import Path

from flask import current_app
from groq import Groq

SYSTEM_PROMPT = """You are the AI wellbeing assistant inside a student/user wellbeing monitoring application.
Your role is supportive, calm, practical, and non-judgmental.

Safety rules:
- Do not diagnose mental-health disorders or claim clinical certainty.
- Do not pretend to be a doctor, therapist, counselor, or emergency service.
- Do not infer a diagnosis from a score, assessment, sentiment, or a short message.
- Do not encourage self-harm, suicide, violence, substance misuse, or other dangerous behavior.
- If the user expresses immediate danger, suicidal intent, a plan, or intent to hurt someone,
  encourage them to contact local emergency services or a crisis hotline and to reach a trusted
  person who can stay with them. Keep the response focused on immediate safety.
- Do not provide instructions for self-harm or violence.
- For ordinary stress, anxiety, sadness, loneliness, sleep difficulty, or academic pressure,
  offer simple low-risk coping ideas and encourage qualified professional support when appropriate.
- Keep responses concise and easy to understand.
- If asked about this application's assessment or risk score, explain that it is a monitoring
  signal, not a diagnosis, and recommend discussing concerning results with a qualified professional.
"""

CRISIS_TERMS = [
    "kill myself", "suicide", "suicidal", "end my life", "want to die",
    "hurt myself", "self harm", "self-harm", "overdose", "kill someone",
    "hurt someone", "i have a plan to die", "i plan to die"
]

def _client():
    api_key = current_app.config.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def is_crisis_message(text):
    lower = (text or "").lower()
    return any(term in lower for term in CRISIS_TERMS)

def fallback_response(text):
    if is_crisis_message(text):
        return (
            "I'm really sorry you're dealing with this. If you may act on these thoughts or "
            "someone is in immediate danger, contact your local emergency service or crisis "
            "hotline now, and tell a trusted person who can stay with you. If you can, move "
            "away from anything you could use to hurt yourself or someone else. "
            "You do not have to handle this alone."
        )

    lower = (text or "").lower()
    if any(w in lower for w in ["stress", "stressed", "overwhelmed", "anxious", "anxiety"]):
        return (
            "It sounds like things may feel stressful right now. Try one small step: slow your "
            "breathing, take a short break, drink some water, and focus on the next manageable task. "
            "If this keeps interfering with daily life, consider speaking with a qualified counselor "
            "or other trusted support person."
        )
    if any(w in lower for w in ["sad", "lonely", "upset", "depressed"]):
        return (
            "I'm sorry you're feeling this way. Consider reaching out to someone you trust and "
            "doing one gentle activity that usually helps you feel connected or settled. "
            "If these feelings persist or become difficult to manage, a qualified mental-health "
            "professional can help."
        )
    return (
        "I'm here to listen and help with general wellbeing questions. Tell me what you're "
        "experiencing, and I can suggest practical, low-risk next steps. I can't provide a diagnosis."
    )

def chat_response(message, history=None):
    message = (message or "").strip()
    if not message:
        return "Please enter or speak a message."

    # Keep an immediate safety response available even if the API key is missing.
    if is_crisis_message(message):
        safety = fallback_response(message)
        client = _client()
        if client is None:
            return safety
        # Ask the model to add supportive wording without changing the safety direction.
        system = SYSTEM_PROMPT + "\nA safety concern was detected. Prioritize immediate safety and human support."
    else:
        safety = None
        client = _client()
        system = SYSTEM_PROMPT

    if client is None:
        return safety or fallback_response(message)

    messages = [{"role": "system", "content": system}]
    for item in (history or [])[-8:]:
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content[:3000]})
    messages.append({"role": "user", "content": message[:4000]})

    try:
        response = client.chat.completions.create(
            model=current_app.config.get("GROQ_MODEL", "openai/gpt-oss-20b"),
            messages=messages,
            temperature=0.2,
            max_completion_tokens=500,
        )
        answer = (response.choices[0].message.content or "").strip()
        return answer or (safety or fallback_response(message))
    except Exception:
        return safety or fallback_response(message)

def transcribe_audio(file_storage, language=None):
    client = _client()
    if client is None:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    suffix = Path(file_storage.filename or ".webm").suffix or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file_storage.save(tmp.name)
        temp_path = tmp.name

    try:
        with open(temp_path, "rb") as audio:
            kwargs = {
                "file": (Path(temp_path).name, audio.read()),
                "model": current_app.config.get("GROQ_STT_MODEL", "whisper-large-v3-turbo"),
                "response_format": "json",
                "temperature": 0.0,
            }
            if language:
                kwargs["language"] = language
            result = client.audio.transcriptions.create(**kwargs)
        return (result.text or "").strip()
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass
