import os
import logging  # Add logging import

# Ensure the necessary directories exist
os.makedirs('data/chat_history', exist_ok=True)
os.makedirs('data/user_data', exist_ok=True)
os.makedirs('data/multi_user_conversations', exist_ok=True)

def trim_conversation_history(history, max_messages=5):
    """Trims the conversation history to the last few messages to stay within token limits."""
    messages = history.split('\n')
    if len(messages) > max_messages * 2:
        return '\n'.join(messages[-max_messages * 2:])
    return history

def save_conversation_history(user_id, history):
    """Saves the conversation history for a user to a file."""
    with open(f"data/chat_history/conversation_history_{user_id}.txt", "w", encoding="utf-8") as file:
        file.write(history)

def load_conversation_history(user_id):
    """Loads the conversation history for a user from a file."""
    try:
        with open(f"data/chat_history/conversation_history_{user_id}.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

def save_important_info(user_id, info):
    """Saves important information for a user to a separate file."""
    logging.info(f"Saving important info for user {user_id}")
    with open(f"data/user_data/important_info_{user_id}.txt", "a", encoding="utf-8") as file:
        file.write(info + "\n")

def load_important_info(user_id):
    """Loads important information for a user from a separate file."""
    try:
        with open(f"data/user_data/important_info_{user_id}.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

def save_multi_user_conversation(conversation_id, context):
    """Saves conversation history for a multi-user conversation."""
    with open(f"data/multi_user_conversations/conversation_{conversation_id}.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(context))
