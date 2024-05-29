import openai
import os
import logging
from personality import personality
from .history import save_conversation_history, trim_conversation_history, save_important_info, load_important_info

openai.api_key = os.getenv('OPENAI_API_KEY')

user_data = {}
important_data = {}  # Define important_data

# Configure logging
logging.basicConfig(level=logging.INFO)

def is_information_request(text):
    """Determines if the text is requesting user information."""
    request_keywords = ["what do you know about me", "tell me about", "information on", "details about"]
    return any(keyword in text.lower() for keyword in request_keywords)

async def analyze_and_extract_important_info(text, existing_info):
    """Uses GPT to analyze text and extract important information."""
    try:
        prompt = f"Existing information: {existing_info}\nNew information: {text}\n\nCompare the new information with the existing information and update it. If there are conflicting details, replace the old ones with the new ones. Provide the updated information in a consistent format."

        logging.info(f"Sending request to GPT-3.5-turbo: {prompt}")

        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a backend process. Extract and update important information such as names, locations, occupations, interests, and any other relevant personal details from the following text. If there is no relevant personal information, respond with an empty message."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()

        logging.info(f"Response from GPT-3.5-turbo: {response_text}")

        # Ensure only non-empty messages are processed
        if not response_text or response_text.lower().startswith("empty message"):
            return "" # Return empty string if no relevant information is found

        return response_text
    except Exception as e:
        logging.error(f"Error analyzing text: {e}")
        return ""

async def generate_response(prompt, user_id, context=[]):
    """Generates a response using OpenAI's API based on the given prompt and user ID."""
    user_history = user_data.get(user_id, "") + '\n'.join(context)
    important_info = load_important_info(user_id)

    logging.info(f"Loaded important info for user {user_id}: {important_info}")

    if is_information_request(prompt):
        # If the message requests user information, use GPT-3.5-turbo to extract and include important info
        important_info = await analyze_and_extract_important_info(important_info, important_info)
        if important_info:
            messages = [
                {"role": "system", "content": personality},
                {"role": "system", "content": f"User information: {important_info}"},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = [
                {"role": "system", "content": personality},
                {"role": "user", "content": prompt}
            ]
    else:
        messages = [
            {"role": "system", "content": personality},
            {"role": "system", "content": f"User information: {important_info}"},  # Include user information in the context
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
        
        # Use GPT to analyze and extract important information
        if not is_information_request(prompt):
            extracted_info = await analyze_and_extract_important_info(prompt, important_info)
            if extracted_info:  # Only save if non-empty
                save_important_info(user_id, extracted_info)
                important_data[user_id] = important_data.get(user_id, "") + extracted_info + "\n"
                logging.info(f"Important info saved for user {user_id}: {extracted_info}")
            
        return response_text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process that request."
