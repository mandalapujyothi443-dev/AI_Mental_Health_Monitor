from flask import current_app

def analyze_text(text):
    """
    Optional Groq analysis. The returned text is a supportive summary,
    not a medical diagnosis.
    """
    if not text:
        return "No optional text was provided."

    api_key = current_app.config.get("GROQ_API_KEY")
    if not api_key:
        return local_text_summary(text)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        prompt = f"""
You are assisting a wellbeing monitoring prototype.
Analyze the following voluntary check-in text for broad emotional indicators.
Do not diagnose any mental-health disorder. Do not make clinical claims.
Return 2-3 short sentences describing observable emotional themes and
suggesting that a qualified human professional can review concerning changes.

Text:
{text}
"""
        response = client.chat.completions.create(
            model=current_app.config["GROQ_MODEL"],
            messages=[
                {"role": "system", "content": "Be careful, supportive, concise, and non-diagnostic."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=180
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return local_text_summary(text)

def local_text_summary(text):
    lower = text.lower()
    concern_words = [
        "stress", "stressed", "anxious", "anxiety", "fear",
        "worried", "sad", "upset", "sleep", "overwhelmed",
        "lonely", "panic", "distress"
    ]
    found = [w for w in concern_words if w in lower]
    if found:
        return (
            "The check-in contains words associated with emotional strain "
            f"({', '.join(found[:5])}). Consider reviewing the trend with a qualified support person."
        )
    return "No obvious concern keywords were detected by the simple local text check."
