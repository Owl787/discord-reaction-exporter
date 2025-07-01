import discord
from discord.ext import commands
import os

TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)
    message = await channel.fetch_message(MESSAGE_ID)

    all_user_ids = set()

    for reaction in message.reactions:
        async for user in reaction.users():
            if not user.bot:
                all_user_ids.add(user.id)

    for user_id in all_user_ids:
        print(f"#p {user_id}")

    await bot.close()

bot.run(TOKEN)
