import spacy
import openai
import os
import logging
from personality import personality
from .history import save_conversation_history, trim_conversation_history, save_important_info, load_conversation_history

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

openai.api_key = os.getenv('OPENAI_API_KEY')

user_data = {}
important_data = {}  # Define important_data

# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_entities(text):
    """Extracts entities from text using spaCy's NER."""
    doc = nlp(text)
    entities = {ent.label_: ent.text for ent in doc.ents}
    return entities

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
        
        # Extract entities and save as important information
        entities = extract_entities(response_text)
        if entities:
            entity_info = " ".join([f"{key}: {value}" for key, value in entities.items()])
            save_important_info(user_id, entity_info)
            important_data[user_id] = important_data.get(user_id, "") + entity_info + "\n"
            logging.info(f"Important entities saved for user {user_id}: {entity_info}")
            
        return response_text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process that request."
