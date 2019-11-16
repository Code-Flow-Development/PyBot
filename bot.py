import discord
import os
import time
from discord.ext import commands
import utils
from dotenv import load_dotenv

# Create a new 'bot' with prefix
bot = commands.Bot(command_prefix="{", description="PyBot")

# Loads commands from commands folder, no need to touch this when adding new commands, it loads them automagically!
if __name__ == '__main__':
    utils.loadallcogs(bot)


# Ready event
@bot.event
async def on_ready():
    bot.startedAt = time.time()
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator}')
    await bot.change_presence(
        activity=discord.Activity(name='in ' + str(len(bot.guilds)) + " server!", type=discord.ActivityType.playing))


# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
