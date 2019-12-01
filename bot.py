import discord
import os
import time
import redis
import json
from threading import Thread
from flask_session import Session
from requests_oauthlib import OAuth2Session
from flask import Flask, jsonify, session, request
from functools import partial
from discord.ext import commands
from bson.json_util import dumps
from dotenv import load_dotenv
from config import getLogger, PREFIX, APIServer, getMongoClient
from utils import ServerSettings, loadAllCogs, loadAllExtensions, UserProfiles

# create flask app
app = Flask(__name__)

# load redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# load redis for sessions
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)

# load env variables
OAUTH2_CLIENT_ID = os.getenv("CLIENT_ID", "")
OAUTH2_CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

app.config['SESSION_TYPE'] = 'redis'
app.config["SESSION_REDIS"] = redis_client
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
sess = Session()

API_VERSION = os.getenv('API_VERSION')

BASE_URL = os.getenv("BASE_URL", "127.0.0.1:5000")
REDIRECT_URI = f"{BASE_URL}/api/{API_VERSION}/login/callback"
TOKEN_URL = "https://discordapp.com/api/oauth2/token"

# Create a new 'bot' with prefix
bot = commands.Bot(command_prefix=PREFIX, description="PyBot")
bot.remove_command('help')
bot.remove_listener(func=bot.on_message)


def worker():
    for guild in bot.guilds:
        ServerSettings(guild)


# Ready event
@bot.event
async def on_ready():
    bot.startedAt = time.time()
    getLogger().info(f'Logged in as {bot.user}')
    # await bot.change_presence(activity=discord.Activity(name='in ' + str(len(bot.guilds)) + " servers!", type=discord.ActivityType.playing))
    await bot.change_presence(activity=discord.Activity(name="hentai! 😳", type=discord.ActivityType.watching),
                              status=discord.Status.dnd)

    # Load cogs
    loadAllCogs(bot)

    # load extensions
    loadAllExtensions(bot)

    # Start the flask api
    partial_run = partial(app.run, host=os.getenv("API_HOST"), port=os.getenv("API_PORT"), debug=True,
                          use_reloader=False)
    APIServer(partial_run).start()

    # Create server documents for each server
    thread = Thread(target=worker, daemon=True)
    thread.start()


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_profile = UserProfiles(message.author).getUserProfile()
    if message.content.startswith(PREFIX):
        if not user_profile["MiscData"]["is_banned"]:
            await bot.process_commands(message)
    else:
        server_settings = ServerSettings(message.guild)
        server_document = server_settings.getServerDocument()
        message_responses_enabled = server_document["message_responses_enabled"]
        counting_channel_enabled = server_document["counting_channels_enabled"]

        if counting_channel_enabled:
            if message.channel.type == discord.ChannelType.text and message.channel.name.lower().startswith(
                    "count-to-"):
                try:
                    # try to convert the string to a number
                    number = int(message.content)
                    next_number = int(message.channel.name.split("-")[-1])
                    if number == next_number and next_number >= 0:
                        # user gave the correct next number
                        await message.channel.edit(name=f"count-to-{number + 1}")
                    elif int(next_number - 2) == number and next_number >= 0:
                        await message.channel.edit(name=f"count-to-{next_number - 1}")
                    else:
                        # not the next number so delete the message
                        await message.delete()
                except ValueError:
                    # not a valid number so delete the message
                    await message.delete()

        if message_responses_enabled:
            custom_message_responses = server_document["custom_message_responses"]
            for custom_response in custom_message_responses:
                trigger = custom_response["trigger"]
                response = custom_response["response"]
                if trigger in message.content.lower():
                    await message.channel.send(response)
                    return


@app.route("/api/v1/users")
def api_users():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                user_collection = getMongoClient()["PyBot"]["users"]
                users = []
                for user in user_collection.find():
                    user_json = json.loads(dumps(user))
                    x = bot.get_user(user_json["id"])
                    users.append({"username": x.name, "id": x.id, "discriminator": x.discriminator,
                                  "avatar_url": str(x.avatar_url),
                                  "is_banned": UserProfiles(x).getUserProfile()["MiscData"]["is_banned"]})
                return jsonify(users)
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/servers")
def api_servers():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                servers = [{"name": x.name, "id": x.id, "region": x.region.name, "icon_url": str(x.icon_url),
                            "voice_channel_amount": len(x.voice_channels), "text_channel_amount": len(x.text_channels),
                            "category_amount": len(x.categories), "member_count": x.member_count,
                            "role_amount": len(x.roles)}
                           for x in bot.guilds]
                return jsonify(servers)
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/server/<int:server_id>")
def api_get_server(server_id):
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                server = bot.get_guild(server_id)
                if server is not None:
                    return jsonify(
                        {"name": server.name, "id": server.id, "region": server.region.name,
                         "icon_url": str(server.icon_url),
                         "voice_channel_amount": len(server.voice_channels),
                         "text_channel_amount": len(server.text_channels),
                         "category_amount": len(server.categories), "member_count": server.member_count,
                         "role_amount": len(server.roles),
                         "text_channels": [{"name": y.name, "id": y.id} for y in server.text_channels],
                         "roles": [{"name": z.name, "id": z.id} for z in server.roles if z.name != "@everyone"]})
                else:
                    return "", 400
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/user/<int:user_id>")
def api_get_user(user_id):
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                user = bot.get_user(user_id)
                if user is not None:
                    return jsonify({"username": user.name, "id": user.id, "discriminator": user.discriminator,
                                    "avatar_url": str(user.avatar_url),
                                    "is_banned": UserProfiles(user).getUserProfile()["MiscData"]["is_banned"]})
                else:
                    return "", 400
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
