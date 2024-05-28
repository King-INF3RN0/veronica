import openai
import os
import logging
from personality import personality
from .history import save_conversation_history, trim_conversation_history, save_important_info, load_conversation_history, load_important_info

openai.api_key = os.getenv('OPENAI_API_KEY')

user_data = {}
important_data = {}  # Define important_data

# Configure logging
logging.basicConfig(level=logging.INFO)

def is_information_request(text):
    """Determines if the text is requesting user information."""
    request_keywords = ["what do you know about me", "tell me about", "information on", "details about"]
    return any(keyword in text.lower() for keyword in request_keywords)

async def analyze_and_extract_important_info(text):
    """Uses GPT to analyze text and extract important information."""
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use a cheaper model if needed
            messages=[
                {"role": "system", "content": "Extract important information such as names, locations, occupations, interests, and any other relevant personal details from the following text."},
                {"role": "user", "content": text}
            ],
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()

        # Check if the response indicates insufficient information
        if await check_insufficient_information(response_text):
            return ""  # Return empty string if insufficient information is detected

        return response_text
    except Exception as e:
        logging.error(f"Error analyzing text: {e}")
        return ""

async def check_insufficient_information(response_text):
    """Uses GPT to determine if the response indicates insufficient information."""
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use a cheaper model if needed
            messages=[
                {"role": "system", "content": "Does the following text indicate that there is insufficient information to extract personal details? Respond with 'yes' or 'no'."},
                {"role": "user", "content": response_text}
            ],
            max_tokens=10
        )
        check_response = completion.choices[0].message.content.strip().lower()
        return check_response == "yes"
    except Exception as e:
        logging.error(f"Error checking for insufficient information: {e}")
        return False

async def generate_response(prompt, user_id, context=[]):
    """Generates a response using OpenAI's API based on the given prompt and user ID."""
    user_history = user_data.get(user_id, "") + '\n'.join(context)
    important_info = load_important_info(user_id)

    if is_information_request(prompt):
        # If the message requests user information, use GPT-3.5-turbo to extract and include important info
        important_info = await analyze_and_extract_important_info(important_info)
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
        if not is_information_request(prompt):
            extracted_info = await analyze_and_extract_important_info(prompt)
            if extracted_info:
                save_important_info(user_id, extracted_info)
                important_data[user_id] = important_data.get(user_id, "") + extracted_info + "\n"
                logging.info(f"Important info saved for user {user_id}: {extracted_info}")
            
        return response_text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process that request."
