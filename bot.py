import os
import discord
from discord.ext import commands
from collections import defaultdict
from dotenv import load_dotenv
import time

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CONTROL_CHANNEL_ID = 1389276377890684948  # Replace with your control channel ID

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='P', intents=intents)

tracked_reactions = defaultdict(set)  # Store reactions per message
user_cooldowns = defaultdict(lambda: 0)  # Store user cooldown timestamps

COOLDOWN_SECONDS = 25

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_raw_reaction_add(payload):
    user_id = payload.user_id
    message_id = payload.message_id

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
            await message.channel.send(f"⚠️ Message ID `{msg_id}` not found.")
            return

        reacted_users = list(tracked_reactions[msg_id])
        already_sent = set()

        for uid in reacted_users:
            if uid not in already_sent:
                await message.channel.send(f"P {uid}")
                already_sent.add(uid)

        for uid in reacted_users:
            for other_uid in reacted_users:
                if other_uid != uid and other_uid not in already_sent:
                    await message.channel.send(f"P {other_uid}")
                    already_sent.add(other_uid)

    except Exception as e:
        await message.channel.send(f"❌ Error: {e}")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in .env file!")

bot.run(TOKEN)
