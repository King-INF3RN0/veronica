import datetime

async def count_active_users(channel, time_frame=10):
    """Counts the number of active users in the channel within the specified time frame."""
    now = datetime.datetime.utcnow().replace(tzinfo=None)
    active_users = set()
    async for message in channel.history(limit=100):
        message_time = message.created_at.replace(tzinfo=None)
        if (now - message_time).total_seconds() <= time_frame * 60:
            active_users.add(message.author.id)
    return len(active_users)

async def is_active_chat(channel, time_frame=60):
    """Checks if the chat is active based on recent messages within the specified time frame."""
    now = datetime.datetime.utcnow().replace(tzinfo=None)
    recent_messages = []
    async for message in channel.history(limit=100):
        message_time = message.created_at.replace(tzinfo=None)
        if (now - message_time).total_seconds() <= time_frame * 60:
            recent_messages.append(message.author.id)
    return len(set(recent_messages)) > 1
