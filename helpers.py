import datetime
import openai
import os
import discord  # Import discord to use its functionality
import random
import asyncio  # Import asyncio for sleep and asynchronous tasks
from personality import personality

openai.api_key = os.getenv('OPENAI_API_KEY')

user_data = {}
conversation_state = {}

def trim_conversation_history(history, max_messages=5):
    messages = history.split('\n')
    if len(messages) > max_messages * 2:
        return '\n'.join(messages[-max_messages * 2:])
    return history

def save_conversation_history(user_id, history):
    with open(f"data/chat_history/conversation_history_{user_id}.txt", "w", encoding="utf-8") as file:
        file.write(history)

def load_conversation_history(user_id):
    try:
        with open(f"data/chat_history/conversation_history_{user_id}.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

async def generate_response(prompt, user_id):
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

async def count_active_users(channel, time_frame=10):
    now = datetime.datetime.utcnow().replace(tzinfo=None)
    active_users = set()
    async for message in channel.history(limit=100):
        message_time = message.created_at.replace(tzinfo=None)
        if (now - message_time).total_seconds() <= time_frame * 60:
            active_users.add(message.author.id)
    return len(active_users)

async def is_active_chat(channel, time_frame=60):
    now = datetime.datetime.utcnow().replace(tzinfo=None)
    recent_messages = []
    async for message in channel.history(limit=100):
        message_time = message.created_at.replace(tzinfo=None)
        if (now - message_time).total_seconds() <= time_frame * 60:
            recent_messages.append(message.author.id)
    return len(set(recent_messages)) > 1

async def random_chat_interjections(client):
    await client.wait_until_ready()
    channel = discord.utils.get(client.get_all_channels(), name='general')  # Change 'general' to your preferred channel name
    while not client.is_closed():
        await asyncio.sleep(random.randint(3600, 10800))  # Random interval between 1 to 3 hours
        if await is_active_chat(channel):
            messages = [
                {"role": "system", "content": personality},
                {"role": "user", "content": "Say something funny or interesting."}
            ]
            try:
                completion = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=75
                )
                response_text = completion.choices[0].message.content.strip()
                await channel.send(response_text)
            except Exception as e:
                print(f"Error generating interjection: {e}")
