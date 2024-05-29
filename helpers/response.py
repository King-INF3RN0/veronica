import openai
import os
import logging
from personality import personality
from .history import save_conversation_history, trim_conversation_history

openai.api_key = os.getenv('OPENAI_API_KEY')

user_data = {}
important_data = {}  # Define important_data

# Configure logging
logging.basicConfig(level=logging.INFO)

async def generate_response(prompt, user_id, context=[]):
    """Generates a response using OpenAI's API based on the given prompt and user ID."""
    user_history = user_data.get(user_id, "") + '\n'.join(context)

    messages = [
        {"role": "system", "content": personality},
        {"role": "user", "content": prompt}
    ]

    try:
        logging.info(f"Sending request to GPT-4o: {messages}")

        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()

        logging.info(f"Response from GPT-4o: {response_text}")

        user_history = f"{user_history}User: {prompt}\nVeronica: {response_text}\n"
        user_history = trim_conversation_history(user_history)
        save_conversation_history(user_id, user_history)
        
        return response_text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process that request."
