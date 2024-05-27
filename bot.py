import discord
import os
from dotenv import load_dotenv
from personality import handle_response
from helpers import generate_response, random_chat_interjections, count_active_users

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')
    discord_client.loop.create_task(random_chat_interjections(discord_client))

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    user_id = message.author.id

    if discord_client.user in message.mentions or discord_client.user.name.lower() in message.content.lower():
        prompt = message.content.replace(f'@{discord_client.user.name}', '').strip()
        if prompt:
            response = await generate_response(prompt, user_id)
            active_users = await count_active_users(message.channel)
            if active_users > 2:
                await message.channel.send(f"<@{user_id}> {response}")
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
