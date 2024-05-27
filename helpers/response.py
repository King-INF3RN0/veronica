import openai
import os
from personality import personality
from .history import save_conversation_history, trim_conversation_history

openai.api_key = os.getenv('OPENAI_API_KEY')

user_data = {}

async def generate_response(prompt, user_id):
    """Generates a response using OpenAI's API based on the given prompt and user ID."""
    user_history = user_data.get(user_id, "")
    messages = [
        {"role": "system", "content": personality},
        {"role": "user", "content": prompt}
    ]
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()
        user_history = f"{user_history}User: {prompt}\nVeronica: {response_text}\n"
        user_history = trim_conversation_history(user_history)
        save_conversation_history(user_id, user_history)
        return response_text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I couldn't process that request."
