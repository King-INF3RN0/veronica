import random
import asyncio
import discord
from .active_users import is_active_chat, count_active_users  # Import count_active_users
from personality import personality
import openai

async def random_chat_interjections(client):
    """Sends random interjections in the chat at random intervals if the chat is active."""
    await client.wait_until_ready()
    channel = discord.utils.get(client.get_all_channels(), name='general')  # Change 'general' to your preferred channel name
    while not client.is_closed():
        await asyncio.sleep(random.randint(3600, 10800))  # Random interval between 1 to 3 hours
        active_users = await count_active_users(channel, time_frame=30)  # Adjust time frame as needed
        if active_users > 1:  # Ensure the chat is active with more than one user
            if not await is_active_chat(channel, time_frame=5):  # Ensure no ongoing conversation in the last 5 minutes
                messages = [
                    {"role": "system", "content": personality},
                    {"role": "user", "content": "Join the conversation naturally with something funny or interesting."}
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
