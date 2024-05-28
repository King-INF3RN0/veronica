import openai
import os
import logging
from personality import personality
from helpers.history import save_conversation_history, trim_conversation_history, save_important_info, load_conversation_history, load_important_info
from helpers.analysis import analyze_message_with_model, handle_user_data, analyze_and_extract_important_info

openai.api_key = os.getenv('OPENAI_API_KEY')

user_data = {}
important_data = {}  # Define important_data

# Configure logging
logging.basicConfig(level=logging.INFO)

async def generate_response(prompt, user_id, context=[]):
    """Generates a response using OpenAI's API based on the given prompt and user ID."""
    user_history = user_data.get(user_id, "") + '\n'.join(context)

    # Process the message with GPT-3.5-turbo to determine the action type
    action_type, gpt35_response = await analyze_message_with_model(prompt)
    
    # Handle user data based on the determined action type
    prompt = await handle_user_data(action_type, user_id, prompt)

    messages = [
        {"role": "system", "content": personality},
        {"role": "user", "content": prompt}
    ]

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()
        user_history = f"{user_history}User: {prompt}\nVeronica: {response_text}\n"
        user_history = trim_conversation_history(user_history)
        save_conversation_history(user_id, user_history)
        
        # Save important info if applicable
        if action_type == "b" or action_type == "c":
            extracted_info = await analyze_and_extract_important_info(prompt)
            if extracted_info:
                save_important_info(user_id, extracted_info)
                important_data[user_id] = important_data.get(user_id, "") + extracted_info + "\n"
                logging.info(f"Important info saved for user {user_id}: {extracted_info}")
            
        return response_text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process that request."
