import discord
import os
import time
import utils
import json
from discord.ext import commands
from dotenv import load_dotenv
from config import getLogger, PREFIX

# Create a new 'bot' with prefix
bot = commands.Bot(command_prefix=PREFIX, description="PyBot")
bot.remove_command('help')

# Loads cogs from cogs folder, no need to touch this when adding new cogs, it loads them automagically!
if __name__ == '__main__':
    utils.loadAllCogs(bot)
    utils.loadAllExtensions(bot)

# Ready event
@bot.event
async def on_ready():
    bot.startedAt = time.time()
    getLogger().info(f'Logged in as {bot.user.name}#{bot.user.discriminator}')
    await bot.change_presence(
        activity=discord.Activity(name='in ' + str(len(bot.guilds)) + " server!", type=discord.ActivityType.playing))


# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
