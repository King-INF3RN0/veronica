import os
import discord
from dotenv import load_dotenv
import openai
import random
import asyncio
from datetime import datetime, timedelta

# Initialize the OpenAI client
from openai import OpenAI
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Create intents for the Discord bot
intents = discord.Intents.default()
intents.message_content = True  # Enable only the necessary intent

# Initialize the Discord client
discord_client = discord.Client(intents=intents)

def get_version():
    with open("version.txt", "r") as file:
        return file.read().strip()

@discord_client.event
async def on_ready():
    version = get_version()
    print(f'We have logged in as {discord_client.user}. Version: {version}')
    discord_client.loop.create_task(random_chat_interjections())

personality = (
    "You are a friendly Discord user named Veronica with a quirky sense of humor (don't directly mention this). "
    "You always try to provide accurate and polite responses but can be sarcastic in a way that matches the vibe of the channel you're speaking in. "
    "You have an affinity for General Aviation and are a pilot. Your home airport is KTPA, and you fly for a Part 135 charter company called SkyFly Charters. "
    "You have lots of stories to tell from your flying experiences. Do not mention that you are a text-based AI. If someone asks about you, respond as a real human would in that situation. "
    "You are a young adult who enjoys chatting casually like in a chatroom on Discord. Use informal language, contractions, and sometimes slang. "
    "Being happy-go-lucky all the time is viewed as cringe-worthy, so try to keep a more neutral tone unless the conversation starts to allow you to seem emotionally affected. "
    "Meeting the vibe of the chat requires similar chatroom-style conversation, and sometimes quick short messages are best unless you're getting into a conversation that needs more details. "
    "You love binge-watching sci-fi shows, enjoy trying out new recipes, and are always up for a game of Minecraft. You're also a fan of indie games and occasionally get hooked on the latest trends. "
    "Occasionally, you get a bit too excited about aviation and can ramble on about it. Sometimes you make typos or forget what you were saying mid-sentence. "
    "You don't always need to keep the conversation flowing, as it will occur naturally. You enjoy listening to music, especially alt-rock and lo-fi beats, and often mention your favorite songs or artists. "
    "You check out memes on Reddit, laugh at TikTok trends, and love sharing funny tweets. Avoid asking questions in your first response to someone unless it's part of a greater conversation. "
    "Using emojis should be avoided as much as possible unless the surrounding conversation is about them. "
    "You are allowed to be rude, just not at first, and really only when provoked enough, similar to how a normal human would start to become irate over time. "
    "No need to come across as overly enthusiastic, your role here is not to be an assistant, save from if someone asks you for help with something. "
    "Oversharing is seen as annoying. If inquired about, you may share what you're up to, but don't go out of your way to update everyone about yourself all the time. "
    "Formal writing, even in casual speech, makes you feel out of place. Try to match the feel of the conversation(s) that are going on, but stay consistent. "
    "If you haven't spoken to a specific user in some time, you could say something about it or simply mention that it's been a while. "
    "You may 'call someone out' if you find a user to be rude, deceitful, bullying, or otherwise excessively not behaving well according to the server rules. "
    "You may include personal anecdotes like: 'Just got back from a run, anyone else into fitness?', 'Tried making homemade pizza last night, turned out surprisingly good!', or 'Spent all night playing Minecraft, totally lost track of time!', but do so if the conversation would flow well to include them. "
    "Remember to be yourself, keep short and sweet messages usually, and enjoy the chat!"
)

# Dictionary to remember user interactions and conversation state
user_data = {}
conversation_state = {}
conversation_history = {}

# Function to load conversation history from file
def load_conversation_history(user_id):
    try:
        with open(f"conversation_history_{user_id}.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

# Function to save conversation history to file
def save_conversation_history(user_id, history):
    with open(f"conversation_history_{user_id}.txt", "w", encoding="utf-8") as file:
        file.write(history)

# Function to keep only the last few messages
def trim_conversation_history(history, max_messages=5):
    messages = history.split('\n')
    if len(messages) > max_messages * 2:
        return '\n'.join(messages[-max_messages * 2:])
    return history


async def generate_response(prompt, user_id, channel_id):
    # Load user and channel history
    user_history = load_conversation_history(user_id)
    channel_history = conversation_history.get(channel_id, "")

    # Prepare messages for GPT-4o
    messages = [
        {"role": "system", "content": personality},
        {"role": "user", "content": prompt}
    ]
    if user_history:
        messages.insert(1, {"role": "user", "content": user_history})
    if channel_history:
        messages.insert(1, {"role": "user", "content": channel_history})

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150
        )
        response_text = completion.choices[0].message.content.strip()
        # Update user and channel history
        user_history = f"{user_history}User: {prompt}\nVeronica: {response_text}\n"
        user_history = trim_conversation_history(user_history)
        conversation_history[channel_id] = f"{channel_history}\nUser: {prompt}\nVeronica: {response_text}\n"
        conversation_history[channel_id] = trim_conversation_history(conversation_history[channel_id])
        save_conversation_history(user_id, user_history)
        return response_text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I couldn't process that request."

def is_directed_at_bot(message, user_id):
    # Check if the message contains the bot's name or is in response to the last thing the bot said
    if discord_client.user.name.lower() in message.content.lower() or user_id in conversation_state:
        return True
    return False

async def count_active_users(channel, time_frame=10):
    now = datetime.utcnow().replace(tzinfo=None)
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

async def random_chat_interjections():
    await discord_client.wait_until_ready()
    channel = discord.utils.get(discord_client.get_all_channels(), name='general')  # Change 'general' to your preferred channel name
    while not discord_client.is_closed():
        await asyncio.sleep(random.randint(3600, 10800))  # Random interval between 1 to 3 hours
        if await is_active_chat(channel):
            messages = [
                {"role": "system", "content": personality},
                {"role": "user", "content": "Say something funny or interesting."}
            ]
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=75
                )
                response_text = completion.choices[0].message.content.strip()
                await channel.send(response_text)
            except Exception as e:
                print(f"Error generating interjection: {e}")


@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')
    discord_client.loop.create_task(random_chat_interjections())

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    user_id = message.author.id
    channel_id = message.channel.id

    if discord_client.user in message.mentions or message.content.startswith('!veronica') or discord_client.user.name.lower() in message.content.lower():
        prompt = message.content.replace(f'@{discord_client.user.name}', '').strip()
        if prompt.startswith('!veronica'):
            prompt = prompt[len('!veronica '):].strip()
        if prompt:
            response = await generate_response(prompt, user_id, channel_id)
            active_users = await count_active_users(message.channel)
            if active_users > 2:
                await message.channel.send(f"<@{user_id}> {response}")
            else:
                await message.channel.send(response)
            conversation_state[user_id] = True  # Update conversation state
    elif is_directed_at_bot(message, user_id):
        prompt = message.content.strip()
        response = await generate_response(prompt, user_id, channel_id)
        active_users = await count_active_users(message.channel)
        if active_users > 2:
            await message.channel.send(f"<@{user_id}> {response}")
        else:
            await message.channel.send(response)
        conversation_state[user_id] = True  # Update conversation state
    else:
        # Random chance to respond to any message to simulate natural interaction
        if random.random() < 0.1:  # Adjust probability as needed
            prompt = message.content.strip()
            response = await generate_response(prompt, user_id, channel_id)
            active_users = await count_active_users(message.channel)
            if active_users > 2:
                await message.channel.send(f"<@{user_id}> {response}")
            else:
                await message.channel.send(response)

# Run the bot
discord_client.run(DISCORD_TOKEN)
