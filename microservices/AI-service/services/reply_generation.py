
import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

# TEMPORARY: load user style from file until DB is ready
with open("user_tones.json", "r") as f:
    USER_STYLE = json.load(f)

def generate_reply(user_id: str, email_body: str) -> str:
    user_tone = USER_STYLE.get(user_id, {}).get("tone", "neutral")
    user_length = USER_STYLE.get(user_id, {}).get("length", "medium")
    user_complexity = USER_STYLE.get(user_id, {}).get("complexity", "moderate")

    prompt = f"Generate a {user_complexity} and {user_length} reply to the following email in a {user_tone} tone:\n\nemail:\n{email_body}\n"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']