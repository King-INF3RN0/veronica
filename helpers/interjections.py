import random
import asyncio
import discord
from .active_users import is_active_chat
from personality import personality
import openai

async def random_chat_interjections(client):
    """Sends random interjections in the chat at random intervals if the chat is active."""
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
                await channel.send(response_text)  # Sends random interjections in the chat at random intervals if the chat is active.
            except Exception as e:
                print(f"Error generating interjection: {e}")
