import openai
import os
import logging
from personality import personality
from .history import save_conversation_history, trim_conversation_history, save_important_info, load_conversation_history

openai.api_key = os.getenv('OPENAI_API_KEY')

user_data = {}
important_data = {}  # Define important_data

# Configure logging
logging.basicConfig(level=logging.INFO)

async def analyze_and_extract_important_info(text):
    """Uses GPT to analyze text and extract important information."""
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use a cheaper model if needed
            messages=[
                {"role": "system", "content": "Extract important information from the following text."},
                {"role": "user", "content": text}
            ],
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()
        return response_text
    except Exception as e:
        logging.error(f"Error analyzing text: {e}")
        return ""

async def generate_response(prompt, user_id, context=[]):
    """Generates a response using OpenAI's API based on the given prompt and user ID."""
    user_history = user_data.get(user_id, "") + '\n'.join(context)
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
        
        # Use GPT to analyze and extract important information
        important_info = await analyze_and_extract_important_info(prompt)
        if important_info:
            save_important_info(user_id, important_info)
            important_data[user_id] = important_data.get(user_id, "") + important_info + "\n"
            logging.info(f"Important info saved for user {user_id}: {important_info}")
            
        return response_text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process that request."
