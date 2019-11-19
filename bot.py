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

# Loads cogs from cogs folder, no need to touch this when adding new cogs, it loads them automagically!
if __name__ == '__main__':
    utils.loadallcogs(bot)


# Ready event
@bot.event
async def on_ready():
    bot.startedAt = time.time()
    getLogger().info(f'Logged in as {bot.user.name}#{bot.user.discriminator}')
    await bot.change_presence(
        activity=discord.Activity(name='in ' + str(len(bot.guilds)) + " server!", type=discord.ActivityType.playing))

    # create datefile for each user
    for member in bot.get_all_members():
        if not member.bot:
            filename = f"data\\{member.id}.json"
            if not os.path.exists(filename):
                file = open(filename, 'w+')
                Data = {
                    "RPGData": {
                        "CreatedCharacter": False,
                        "Name": {
                          "FirstName": "none",
                          "MiddleName": "none",
                          "LastName": "none",
                        },
                        "Inventory": {

                        },
                    },

                    "MiscData": {

                    }
                }
                JSONConverted = json.dumps(Data)
                file.write(JSONConverted)
                file.close()
                getLogger().info(f"Wrote new data file for user `{member.name} ({member.id})`")


# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
