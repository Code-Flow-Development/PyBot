import discord
import os
import time
import redis
import json
from flask_session import Session
from requests_oauthlib import OAuth2Session
from flask import Flask, jsonify, session, request
from functools import partial
from discord.ext import commands
from dotenv import load_dotenv
from config import getLogger, PREFIX, APIServer
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

    for user in bot.users:
        # we need to ensure all users have profiles (mainly for the dashboard to operate correctly), but using the UserProfile function is way to slow for large guilds and it would block the bot util loading finished
        pass


@app.route("/api/v1/users")
def api_users():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                users = [
                    {"username": x.name, "id": x.id, "discriminator": x.discriminator, "avatar_url": str(x.avatar_url),
                     "is_banned": UserProfiles(x).getUserProfile()["MiscData"]["is_banned"]} for
                    x in
                    bot.users if not x.bot]
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


# Loads cogs from cogs folder, no need to touch this when adding new cogs, it loads them automagically!
if __name__ == '__main__':
    loadAllCogs(bot)
    loadAllExtensions(bot)

# run flask in partial
partial_run = partial(app.run, host=os.getenv("API_HOST"), port=os.getenv("API_PORT"), debug=True, use_reloader=False)

# run flask in another thread (multithreading)
APIServer(partial_run).start()

# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
