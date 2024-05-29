import openai
import logging
from .history import load_important_info, save_important_info

# Configure logging
logging.basicConfig(level=logging.INFO)

async def analyze_message_with_model(message_text, model_name="gpt-3.5-turbo"):
    """Process the message with the specified model to determine type and handle user data."""
    try:
        completion = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Determine if the following text is a request for user data, a modification of user data, or both. If it is neither, respond with 'normal message'. Extract any relevant information if applicable."},
                {"role": "user", "content": message_text}
            ],
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()
        
        # Parse response to determine the type of request
        if "request user data" in response_text.lower():
            return "a", response_text
        elif "modify user data" in response_text.lower():
            return "b", response_text
        elif "both request and modify user data" in response_text.lower():
            return "c", response_text
        else:
            return "d", response_text
    except Exception as e:
        logging.error(f"Error processing message with {model_name}: {e}")
        return "d", ""

async def handle_user_data(action_type, user_id, message_text):
    """Handle user data based on the determined action type."""
    if action_type == "a" or action_type == "c":
        # Extract user data
        user_data = load_important_info(user_id)
        if user_data:
            message_text += f"\nUser data: {user_data}"
    if action_type == "b" or action_type == "c":
        # Modify user data
        extracted_info = await analyze_and_extract_important_info(message_text)
        if extracted_info:
            save_important_info(user_id, extracted_info)
    return message_text

async def analyze_and_extract_important_info(text):
    """Uses GPT to analyze text and extract important information."""
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a backend process. Extract important information such as names, locations, occupations, interests, and any other relevant personal details from the following text. If there is no relevant personal information, respond with an empty message."},
                {"role": "user", "content": text}
            ],
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()

        # Ensure only non-empty messages are processed
        if not response_text or response_text.lower().startswith("empty message"):
            return "" # Return empty string if no relevant information is found

        return response_text
    except Exception as e:
        logging.error(f"Error analyzing text: {e}")
        return ""
