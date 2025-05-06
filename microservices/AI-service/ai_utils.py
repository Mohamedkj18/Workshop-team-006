import openai
import os 
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

with open("user_tone.txt", "r") as f:
    USER_STYLE = json.load(f)

def generate_reply(email):
    #Get the user tone from the email
    user_id = email["user_id"]
    user_tone = USER_STYLE.get(user_id, {}).get("tone", "neutral")
    user_length = USER_STYLE.get(user_id, {}).get("length", "medium")
    user_complexity = USER_STYLE.get(user_id, {}).get("complexity", "moderate")

    prompt = f"Generate a {user_complexity} and {user_length} reply to the following email in a {user_tone}:\n\nemail:\n{email['body']}\n"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']
