import os
import json
import requests
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# TEMP fallback until you fully rely on the service
USER_TONES_PATH = os.getenv("USER_TONES_PATH", "user_tones.json")
try:
    with open(USER_TONES_PATH, "r", encoding="utf-8") as f:
        USER_STYLE_FALLBACK = json.load(f)
except Exception:
    USER_STYLE_FALLBACK = {}

USER_STYLE_BASE_URL = os.getenv("USER_STYLE_BASE_URL", "http://user-style-service:8010/api")

TIMEOUT = 6  # seconds

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
    POST /style/get-user-general-style -> {"derived_labels": {...}}
    """
    data = _post_json("/style/get-user-general-style", {"user_id": user_id, "email_text": ""})
    if data and isinstance(data.get("derived_labels"), dict):
        return data["derived_labels"]
    return None  # 404 when no profile exists is expected behavior. :contentReference[oaicite:2]{index=2}

def _get_reply_cluster_labels(user_id: str, incoming_email: str) -> dict | None:
    """
    POST /reply/get-user-reply-style -> {"derived_labels": {...}}
    This endpoint computes features for 'email_text', finds closest cluster, then returns labels. :contentReference[oaicite:3]{index=3}
    """
    data = _post_json("/reply/get-user-reply-style", {"user_id": user_id, "email_text": incoming_email})
    if data and isinstance(data.get("derived_labels"), dict):
        return data["derived_labels"]
    return None

def _fallback_labels(user_id: str) -> dict:
    s = USER_STYLE_FALLBACK.get(user_id, {}) or {}
    # Keep simple keys only. Service derived labels typically include similar fields.
    return {
        "tone": s.get("tone", "neutral"),
        "length": s.get("length", "medium"),
        "complexity": s.get("complexity", "moderate"),
        "formality": s.get("formality", "informal"),
        "processing_style": s.get("processing_style", "inquisitive"),
    }

def _style_block(labels: dict, title: str) -> str:
    return (
        f"{title}:\n"
        f"- Tone: {labels.get('tone','neutral')}\n"
        f"- Length: {labels.get('length','medium')}\n"
        f"- Complexity: {labels.get('complexity','moderate')}\n"
        f"- Formality: {labels.get('formality','informal')}\n"
        f"- Processing style: {labels.get('processing_style','inquisitive')}\n"
    )

def generate_reply(user_id: str, email_body: str) -> str:
    """
    Reply generation using the user-style service API.
    1) Fetch general style labels for the user
    2) Fetch closest reply-cluster labels for the incoming email
    3) Build a prompt that honors both, with the cluster guiding context-specific tweaks
    Falls back to user_tones.json if the service is unreachable.
    """
    if not isinstance(email_body, str) or not email_body.strip():
        return "Invalid email body. Please try again."

    # Try service first
    general_labels = _get_general_style_labels(user_id)
    cluster_labels = _get_reply_cluster_labels(user_id, email_body)

    # If service fails, fall back
    if not general_labels and not cluster_labels:
        general_labels = _fallback_labels(user_id)
        cluster_labels = {}

    # Merge, with cluster cues overriding where provided
    labels = {**(general_labels or {}), **(cluster_labels or {})}

    # Light length guidance for the model
    length_guidance = {
        "short": "Keep it under 120 words if possible.",
        "medium": "Aim for 120 to 220 words.",
        "detailed": "Feel free to go beyond 220 words when helpful.",
    }.get(labels.get("length", "medium"), "Aim for 120 to 220 words.")

    ask_questions = labels.get("processing_style", "").lower() == "inquisitive"

    style_block_general = _style_block(general_labels or {}, "User general style")
    style_block_cluster = _style_block(cluster_labels or {}, "Context cues from closest reply cluster")

    prompt = f"""
You are Lazy Mail generating a reply on behalf of the user. Match their learned style.

{style_block_general}
{style_block_cluster if cluster_labels else ""}

Reply rules:
- This is a reply to the email below. Keep context and answer what was asked.
- Reflect the user's tone and formality. The cluster cues are context-specific and should guide the reply.
- {length_guidance}
- {"Include one or two concise questions for clarification if useful." if ask_questions else "Ask questions only if strictly necessary."}
- Keep passive voice low and maintain a positive, helpful attitude.
- Use clear, short paragraphs. Bullet points are fine for lists.
- Output only the reply body. No prefaces or labels.

Original email:
\"\"\"{email_body.strip()}\"\"\"

Write the reply now.
""".strip()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"]
