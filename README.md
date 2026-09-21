# AI-Powered Dynamic Mental Health Monitoring and Distress Prediction System

A Flask + ML + optional Groq-powered prototype for tracking voluntary mental-wellbeing check-ins over time.

## Safety
This is a prototype decision-support/early-warning system, not a medical diagnostic tool.
Do not use it as a substitute for a qualified mental-health professional or emergency service.
Use synthetic/demo data during development and presentations.

## Features
- User registration/login
- Voluntary wellbeing assessment
- ML-based distress risk estimation
- Optional Groq text analysis
- Historical trend chart
- Counselor/support dashboard
- Alert workflow
- SQLite database
- Basic automated tests

## Setup

Windows:
```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python ml\train_model.py
python app.py
```

Then open http://127.0.0.1:5000

Optional Groq:
1. Put your API key in `.env`:
   GROQ_API_KEY=your_key
2. Restart Flask.

If no Groq key is configured, the application still works using the local ML model and rule-based text fallback.

Demo counselor login:
- Email: counselor@example.com
- Password: Counselor@123

Demo user:
- Email: user@example.com
- Password: User@123

The demo accounts are created automatically by `init_db()`.


## AI Chatbot + Voice Assistant

This version includes a logged-in `/assistant/` page with:
- Groq AI chatbot using `openai/gpt-oss-20b`
- Groq Whisper speech-to-text using `whisper-large-v3-turbo`
- Browser text-to-speech for spoken AI responses
- English, Telugu, Hindi, Tamil, Kannada, and Malayalam voice input selection
- Conversation history in the current browser session
- Safety-focused wellbeing prompt and crisis-response guard
- No API key exposed to browser JavaScript

Set `GROQ_API_KEY` in `.env`, then run `python app.py` and open `/assistant/`.
