import discord
import os
import time
from discord.ext import commands
from dotenv import load_dotenv
from config import getLogger, PREFIX
from utils import ServerSettings, loadAllCogs, loadAllExtensions

# Create a new 'bot' with prefix
bot = commands.Bot(command_prefix=PREFIX, description="PyBot")
bot.remove_command('help')

# Loads cogs from cogs folder, no need to touch this when adding new cogs, it loads them automagically!
if __name__ == '__main__':
    loadAllCogs(bot)
    loadAllExtensions(bot)

# Ready event
@bot.event
async def on_ready():
    bot.startedAt = time.time()
    getLogger().info(f'Logged in as {bot.user}')
    await bot.change_presence(
        activity=discord.Activity(name='in ' + str(len(bot.guilds)) + " servers!", type=discord.ActivityType.playing))
    # Create server documents for each server
    for guild in bot.guilds:
        ServerSettings(guild)


# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
