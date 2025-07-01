import os
import discord
from discord.ext import commands
from collections import defaultdict
import time

TOKEN = os.getenv("DISCORD_TOKEN")  # Make sure this is set in your environment

CONTROL_CHANNEL_ID = 1389308377909166110  # <-- replace with your channel ID

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='P', intents=intents)

tracked_reactions = defaultdict(set)
user_cooldowns = defaultdict(lambda: 0)  # Store per-user last command timestamp
COOLDOWN_SECONDS = 25

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    user_id = payload.user_id

    if user_id == bot.user.id:
        return

    tracked_reactions[message_id].add(user_id)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id != CONTROL_CHANNEL_ID:
        return

    if not message.content.startswith("P "):
        return

    now = time.time()
    last_used = user_cooldowns[message.author.id]

    if now - last_used < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_used))
        await message.channel.send(f"⏳ Please wait {remaining}s before using `P` again.")
        return

    user_cooldowns[message.author.id] = now

    try:
        parts = message.content.strip().split()
        if len(parts) != 2:
            return

        msg_id = int(parts[1])
        if msg_id not in tracked_reactions:
            await message.channel.send(f"⚠️ Message `{msg_id}` not tracked.")
            return

        control_channel = bot.get_channel(CONTROL_CHANNEL_ID)

        # Send P <user_id> for each user who reacted
        for user_id in tracked_reactions[msg_id]:
            await control_channel.send(f"P {user_id}")

        # Send P <user_id> for each user who reacted for another user
        for uid in tracked_reactions[msg_id]:
            for other_uid in tracked_reactions[msg_id]:
                if uid != other_uid:
                    await control_channel.send(f"P {other_uid}")

    except Exception as e:
        await message.channel.send(f"❌ Error: {e}")
