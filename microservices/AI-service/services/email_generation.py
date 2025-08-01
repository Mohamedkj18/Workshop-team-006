import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_email(prompt: str) -> str:
    if not validate_prompt(prompt):
        return "Invalid prompt. Please try again."
    gptPrompt = style_prompt = f"""
        You are writing on behalf of lazy mail user. Their writing style is friendly, moderately complex, and detailed. 
        They prefer an informal tone and tend to ask questions often, reflecting an inquisitive processing style. 
        Their sentences average around 15 words, they rarely use passive voice, and their emails are highly subjective 
        with a generally positive sentiment. The ideal reading grade level is around 6.5.

        Write a response that matches this style.

        Prompt: {prompt}
        """.strip()
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": gptPrompt}]
    )

    return response['choices'][0]['message']['content']

def validate_prompt(prompt: str) -> bool:
    return True