import discord
import os
from dotenv import load_dotenv
from personality import handle_response
from helpers.response import generate_response
from helpers.interjections import random_chat_interjections
from helpers.active_users import count_active_users
from helpers.history import save_important_info  # Add save_important_info import

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')  # Event handler for when the bot is ready and logged in.
    discord_client.loop.create_task(random_chat_interjections(discord_client))  # Start interjections.

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:  # Ignore messages from the bot itself.
        return

    user_id = message.author.id

    if discord_client.user in message.mentions or discord_client.user.name.lower() in message.content.lower():
        prompt = message.content.replace(f'@{discord_client.user.name}', '').strip()
        if prompt:
            response = await generate_response(prompt, user_id)
            active_users = await count_active_users(message.channel)
            if active_users > 2:
                await message.channel.send(f"<@{user_id}> {response}")  # Ping if multiple users are active.
            else:
                await message.channel.send(response)
    elif handle_response(message, user_id):
        prompt = message.content.strip()
        response = await generate_response(prompt, user_id)
        active_users = await count_active_users(message.channel)
        if active_users > 2:
            await message.channel.send(f"<@{user_id}> {response}")
        else:
            await message.channel.send(response)

discord_client.run(DISCORD_TOKEN)
