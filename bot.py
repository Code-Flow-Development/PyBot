import discord
import os
import time
import json
from flask import Flask, jsonify
from functools import partial
from discord.ext import commands
from dotenv import load_dotenv
from config import getLogger, PREFIX, APIServer
from utils import ServerSettings, loadAllCogs, loadAllExtensions

# create flask app
app = Flask(__name__)

# Create a new 'bot' with prefix
bot = commands.Bot(command_prefix=PREFIX, description="PyBot")
bot.remove_command('help')


# Ready event
@bot.event
async def on_ready():
    bot.startedAt = time.time()
    getLogger().info(f'Logged in as {bot.user}')
    # await bot.change_presence(activity=discord.Activity(name='in ' + str(len(bot.guilds)) + " servers!", type=discord.ActivityType.playing))
    await bot.change_presence(activity=discord.Activity(name="hentai! 😳", type=discord.ActivityType.watching),
                              status=discord.Status.dnd)
    # Create server documents for each server
    for guild in bot.guilds:
        ServerSettings(guild)


@app.route("/api/users")
def api_users():
    if bot.is_ready():
        users = [{"username": x.name, "id": x.id, "discriminator": x.discriminator, "avatar": x.avatar} for x in
                 bot.users if not x.bot]
        return jsonify(users)
    else:
        return "bot is not ready!", 500


@app.route("/api/servers")
def api_servers():
    if bot.is_ready():
        servers = [{"name": x.name, "id": x.id, "region": x.region.name, "icon_url": str(x.icon_url),
                    "voice_channel_amount": len(x.voice_channels), "text_channel_amount": len(x.text_channels),
                    "category_amount": len(x.categories), "member_count": x.member_count, "role_amount": len(x.roles)}
                   for x in bot.guilds]
        return jsonify(servers)
    else:
        return "bot is not ready!", 500


# Loads cogs from cogs folder, no need to touch this when adding new cogs, it loads them automagically!
if __name__ == '__main__':
    loadAllCogs(bot)
    loadAllExtensions(bot)

# run flask in partial
partial_run = partial(app.run, port=5001, debug=True, use_reloader=False)

# run flask in another thread (multithreading)
APIServer(partial_run).start()

# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
