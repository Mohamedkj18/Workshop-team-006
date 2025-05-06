import openai
import json
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_email_style(email_text):
    prompt = f"""
        Analyze the following email and determine the writer's typical style.

        Return your answer as a JSON object in the format: {{
        "tone": "...",
        "length": "...",
        "complexity": "..."
        }}

        Tone options: friendly, humorous, empathetic, instructive, assertive, professional, formal, neutral  
        Length options: short, medium, long  
        Complexity options: simple, moderate, complex

        Email:
        \"\"\"
        {email_text}
        \"\"\"
        """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(response['choices'][0]['message']['content'])
    except Exception as e:
        print("Failed to parse response:", response['choices'][0]['message']['content'])
        raise e


def save_user_style(user_id, tone, length, complexity):        
    try:
        with open("user_tones.json", "r+") as f:
            tones = json.load(f)
            tones[user_id] = {"tone": tone, "length": length, "complexity": complexity}
            f.seek(0)
            json.dump(tones, f, indent=2)
            f.truncate()
    except FileNotFoundError:
        with open("user_tones.json", "w") as f:
            json.dump({user_id: {"tone": tone, "length": length, "complexity": complexity}}, f, indent=2)


def learn_user_style(user_id, emails):
    tone_counts = {}
    length_counts = {}
    complexity_counts = {}

    for email in emails:
        response = analyze_email_style(email["body"])
        tone = response.get("tone")
        length = response.get("length")
        complexity = response.get("complexity")

        tone_counts[tone] = tone_counts.get(tone, 0) + 1
        length_counts[length] = length_counts.get(length, 0) + 1
        complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
    
    most_common_tone = max(tone_counts, key=tone_counts.get)
    most_common_length = max(length_counts, key=length_counts.get)
    most_common_complexity = max(complexity_counts, key=complexity_counts.get)

    save_user_style(user_id, most_common_tone, most_common_length, most_common_complexity)
    return (most_common_tone, most_common_length, most_common_complexity)
