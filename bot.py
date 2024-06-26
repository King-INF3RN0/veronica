import discord
import os
import random
import json
from dotenv import load_dotenv
from personality import handle_response
from helpers.response import generate_response
from helpers.history import load_all_important_info, save_important_info, load_important_info, save_multi_user_conversation
from helpers.interjections import random_chat_interjections
from helpers.active_users import count_active_users

conversation_state = {}  # Define conversation state globally
important_data = {}  # Dictionary to store important data

important_data = load_all_important_info()  # Load all important info on startup

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
    nickname = message.author.display_name
    username = message.author.name

    # Save user information if it's the first interaction
    if not os.path.exists(f"data/user_data/important_info_{user_id}.txt"):
        user_info = f"Nickname: {nickname}\nUsername: {username}\n"
        save_important_info(user_id, user_info)

    context = []
    users_involved = set()

    async for msg in message.channel.history(limit=5):
        if msg.author == discord_client.user:
            context.append(f"Veronica: {msg.content}")
        else:
            context.append(f"User: {msg.content}")
            users_involved.add(msg.author.id)

    if len(users_involved) > 2:
        # Save multi-user conversation
        users_involved = list(users_involved)
        users_involved.sort()
        conversation_id = "_".join(map(str, users_involved))
        save_multi_user_conversation(conversation_id, context)
        for user in users_involved:
            context.append(f"{message.author.display_name}: {message.content}")
            save_important_info(user, json.dumps(context))
    else:
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
