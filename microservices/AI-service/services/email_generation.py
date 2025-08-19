import os
import json
import requests
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# Service base URL, eg: http://user-style-service:8010/api
USER_STYLE_BASE_URL = os.getenv("USER_STYLE_BASE_URL", "http://api/user-style-service:8010")
TIMEOUT = 6  # seconds

# TEMP fallback until you fully rely on the service
USER_TONES_PATH = os.getenv("USER_TONES_PATH", "user_tones.json")
try:
    with open(USER_TONES_PATH, "r", encoding="utf-8") as f:
        USER_STYLE_FALLBACK = json.load(f)
except Exception:
    USER_STYLE_FALLBACK = {}

def _post_json(path: str, payload: dict) -> dict | None:
    try:
        url = f"{USER_STYLE_BASE_URL}{path}"
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def _get_general_style_labels(user_id: str) -> dict | None:
    """
    Expects your user-style service to return:
      {"derived_labels": {"tone": "...", "length": "...", "complexity": "...", ...}}
    """
    data = _post_json("/style/get-user-general-style", {"user_id": user_id, "email_text": ""})
    if data and isinstance(data.get("derived_labels"), dict):
        return data["derived_labels"]
    return None

def _fallback_labels(user_id: str) -> dict:
    s = USER_STYLE_FALLBACK.get(user_id, {}) or {}
    return {
        "tone": s.get("tone", "neutral"),
        "length": s.get("length", "medium"),           # short | medium | detailed
        "complexity": s.get("complexity", "moderate"), # simple | moderate | advanced
        "formality": s.get("formality", "informal"),
        "processing_style": s.get("processing_style", "inquisitive"),
        "signature": s.get("signature", None),
        # Optional numeric hints if you have them in the file
        "avg_sentence_length": s.get("avg_sentence_length", 15),
        "reading_grade_level": s.get("reading_grade_level", 6.5),
        "passive_voice_ratio": s.get("passive_voice_ratio", 0.05),
        "question_ratio": s.get("question_ratio", 0.3),
    }

def _style_block(labels: dict) -> str:
    return (
        "User style profile for composition:\n"
        f"- Tone: {labels.get('tone','neutral')}\n"
        f"- Formality: {labels.get('formality','informal')}\n"
        f"- Length: {labels.get('length','medium')}\n"
        f"- Complexity: {labels.get('complexity','moderate')}\n"
        f"- Processing style: {labels.get('processing_style','inquisitive')}\n"
        f"- Typical sentence length ≈ {labels.get('avg_sentence_length', 15)} words\n"
        f"- Reading grade level ≈ {labels.get('reading_grade_level', 6.5)}\n"
        f"- Passive voice ratio ≈ {labels.get('passive_voice_ratio', 0.05)}\n"
        f"- Question ratio ≈ {labels.get('question_ratio', 0.3)}\n"
    )

def generate_email(user_id: str, prompt: str) -> str:
    """
    Compose a brand new email that matches the user's learned style.
    Uses only general style from the user-style service (no cluster logic).
    Returns a string with:
      Subject: ...
      Body:
      ...
    """
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        return "Invalid prompt. Please try again."

    labels = _get_general_style_labels(user_id)
    if not labels:
        labels = _fallback_labels(user_id)

    style_block = _style_block(labels)

    length_guidance = {
        "short": "Keep the body under 120 words if possible.",
        "medium": "Aim for 120 to 220 words in the body.",
        "detailed": "Feel free to go beyond 220 words when helpful.",
    }.get(labels.get("length", "medium"), "Aim for 120 to 220 words in the body.")

    ask_questions = labels.get("processing_style", "").lower() == "inquisitive"
    signature = labels.get("signature")
    signature_line = f"\n\n{signature}" if signature else ""

    gpt_prompt = f"""
You are Lazy Mail composing a new email on behalf of a specific user. Match their learned style exactly.

{style_block}

Composition rules:
- This is a fresh email, not a reply.
- Produce exactly two sections with these headers:
  Subject: <a concise subject line>
  Body:
  <the full email body as short paragraphs and optional bullet points>
- Reflect the user's tone, formality, and typical structure.
- Keep passive voice low and write clearly.
- {length_guidance}
- {"Include one or two concise questions if suitable for the task." if ask_questions else "Ask questions only if they clearly add value."}
- Do not include any preface or explanations beyond the two sections above.

Task:
{prompt.strip()}

Output now. Append the user's signature at the end of the Body only if provided.
""".strip()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": gpt_prompt}],
        temperature=0.7,
    )
    text = response["choices"][0]["message"]["content"]

    # If you want to enforce signature placement consistently, you could append it here
    # only when the model did not already include it. Left as-is for simplicity.

    return text
