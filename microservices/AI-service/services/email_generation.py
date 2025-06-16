import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_email(prompt: str) -> str:
    if not validate_prompt(prompt):
        return "Invalid prompt. Please try again."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']

def validate_prompt(prompt: str) -> bool:
    return True