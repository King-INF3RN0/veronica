import discord
import os
import random
from dotenv import load_dotenv
from personality import handle_response
from helpers.response import generate_response
from helpers.interjections import random_chat_interjections
from helpers.active_users import count_active_users
from helpers.history import save_important_info, load_important_info

conversation_state = {}  # Define conversation state globally
important_data = {}  # Dictionary to store important data

def load_all_important_info():
    """Loads all important information for all users."""
    global important_data
    if not os.path.exists('data/user_data'):
        os.makedirs('data/user_data')
    for filename in os.listdir('data/user_data'):
        if filename.startswith('important_info_'):
            user_id = filename[len('important_info_'):-4]
            important_data[user_id] = load_important_info(user_id)

load_all_important_info()  # Load all important info on startup

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')  # Event handler for when the bot is ready and logged in.
    discord_client.loop.create_task(random_chat_interjections(discord_client))  # Start interjections.

def is_directed_at_bot(message, user_id):
    """Checks if a message is directed at the bot based on conversation state."""
    if user_id in conversation_state:
        return True
    return False

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:  # Ignore messages from the bot itself.
        return

    user_id = message.author.id
    context = []

    async for msg in message.channel.history(limit=5):
        if msg.author == discord_client.user:
            context.append(f"Veronica: {msg.content}")
        else:
            context.append(f"User: {msg.content}")

    if discord_client.user in message.mentions or discord_client.user.name.lower() in message.content.lower():
        prompt = message.content.replace(f'@{discord_client.user.name}', '').strip()
        if prompt:
            response = await generate_response(prompt, user_id, context)
            active_users = await count_active_users(message.channel)
            if active_users > 2:
                await message.channel.send(f"<@{user_id}> {response}")  # Ping if multiple users are active.
            else:
                await message.channel.send(response)
    else:
        prompt = message.content.strip()
        response = await generate_response(prompt, user_id, context)
        active_users = await count_active_users(message.channel)
        if active_users > 2:
            await message.channel.send(f"<@{user_id}> {response}")
        else:
            await message.channel.send(response)
        conversation_state[user_id] = True  # Update conversation state

discord_client.run(DISCORD_TOKEN)
