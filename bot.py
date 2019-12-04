import asyncio
import json
import os
import time
from functools import partial
from threading import Thread
from dotenv import load_dotenv
import discord
import redis
from bson.json_util import dumps
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask, jsonify, session, request
from flask_session import Session
from requests_oauthlib import OAuth2Session
from utils import ServerSettings, loadAllCogs, loadAllExtensions, UserProfiles, SetupLogger, APIServer, getLogger, \
    RedisClient, Mongo

# get asyncio loop
loop = asyncio.get_event_loop()

# create flask app
app = Flask(__name__)

# load dotenv
load_dotenv()

# load env variables
OAUTH2_CLIENT_ID = os.getenv("CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# setup session
app.config['SESSION_TYPE'] = 'redis'
app.config["SESSION_REDIS"] = RedisClient().getRedisClient()
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
sess = Session()

API_VERSION = os.getenv('API_VERSION')

BASE_URL = os.getenv("BASE_URL")
REDIRECT_URI = f"{BASE_URL}/api/{API_VERSION}/login/callback"
TOKEN_URL = "https://discordapp.com/api/oauth2/token"

# get prefix from .env
PREFIX = os.getenv("BOT_PREFIX")

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


# message event
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_profile = UserProfiles(message.author).getUserProfile()
    server_settings = ServerSettings(message.guild).getServerDocument()
    if message.content.startswith(PREFIX):
        if not server_settings["is_banned"] and not user_profile["MiscData"]["is_banned"]:
            await bot.process_commands(message)
    else:
        message_responses_enabled = server_settings["modules"]["message_responses"]
        counting_channel_enabled = server_settings["modules"]["counting_channels"]

        if message.channel.type == discord.ChannelType.text and message.channel.name.lower().startswith(
                "count-to-"):
            if counting_channel_enabled:
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
            custom_message_responses = server_settings["custom_message_responses"]
            for custom_response in custom_message_responses:
                trigger = custom_response["trigger"]
                response = custom_response["response"]
                if trigger in message.content.lower():
                    await message.channel.send(response)
                    return

        # profanity filter
        words = json.loads(open("settings.json", 'r').read())["profanity_words"]
        if any(substring in message.content.lower() for substring in words):
            await message.delete()
            await asyncio.sleep(1)
            await message.channel.send("A word you said is not allowed in this server! :rage:")


@app.route("/api/v1/users", methods=["GET"])
def api_users():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                user_collection = Mongo().getMongoClient()["PyBot"]["users"]
                users = []
                for user in user_collection.find():
                    user_json = json.loads(dumps(user))
                    x = bot.get_user(user_json["id"])
                    users.append({"username": x.name, "id": x.id, "discriminator": x.discriminator,
                                  "avatar_url": str(x.avatar_url),
                                  "is_banned": user_json["MiscData"]["is_banned"]})
                return jsonify(users)
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/servers", methods=["GET"])
def api_servers():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                server_collection = Mongo().getMongoClient()["PyBot"]["servers"]
                servers = []
                for server in server_collection.find():
                    server_json = json.loads(dumps(server))
                    x = bot.get_guild(server_json["id"])
                    servers.append({"name": x.name, "id": x.id, "region": x.region.name, "icon_url": str(x.icon_url),
                                    "voice_channel_amount": len(x.voice_channels),
                                    "text_channel_amount": len(x.text_channels),
                                    "category_amount": len(x.categories), "member_count": x.member_count,
                                    "role_amount": len(x.roles),
                                    "is_banned": server_json["settings"]["is_banned"]})
                return jsonify(servers)
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/admin/leaveServer", methods=["POST"])
def admin_leave_server():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    # leave server
                    server_id = int(request.get_json()["server_id"])
                    guild = bot.get_guild(server_id)
                    if guild is not None:
                        try:
                            leave_fut = asyncio.run_coroutine_threadsafe(
                                guild.leave(),
                                loop
                            )
                            leave_fut.result()
                            ServerSettings(guild).reset()
                            return "Guild left", 200
                        except Exception as e:
                            getLogger().critical(f"Failed to leave guild: {guild.name}; Error: {e}")
                            return "Error leaving guild", 500
                    else:
                        return "Guild is none", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/banServerNotification", methods=["POST"])
def admin_ban_server_notify():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    # leave server
                    server_id = int(request.get_json()["server_id"])
                    guild = bot.get_guild(server_id)
                    if guild is not None:
                        reason = request.get_json()["reason"] if request.get_json()["reason"] != "" else "not specified"
                        # get guild owner
                        try:
                            banner_user = discord_session.get("https://discordapp.com/api/users/@me").json()
                            send_fut = asyncio.run_coroutine_threadsafe(
                                guild.owner.send(
                                    f"Hello {guild.owner.name},\nYour server ``{guild.name}`` has been banned! Members won't be able to use my commands! This ban was issued by ``{banner_user['username']}`` with reason: ``{reason}``."),
                                loop
                            )
                            send_fut.result()
                            return "OK", 200
                        except discord.Forbidden as e:
                            getLogger().error(
                                f"Missing permission to send server ban notification to user {guild.owner} ({guild.owner.id})! Error: {e.text}")
                            return "missing permissions", 500
                        except discord.HTTPException as e:
                            getLogger().error(
                                f"Failed to send server ban notification to user {guild.owner} ({guild.owner.id})! Error: {e.text}")
                            return "failed", 500
                        except discord.InvalidArgument as e:
                            getLogger().error(
                                f"Failed to send server ban notification to user {guild.owner} ({guild.owner.id})! Error: {e}")
                            return "invalid argument, we shouldnt be here?!", 500
                    else:
                        return "Guild is none", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/unbanServerNotification", methods=["POST"])
def admin_unban_server_notify():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    server_id = int(request.get_json()["server_id"])
                    guild = bot.get_guild(server_id)
                    if guild is not None:
                        try:
                            banner_user = discord_session.get("https://discordapp.com/api/users/@me").json()
                            send_fut = asyncio.run_coroutine_threadsafe(
                                guild.owner.send(
                                    f"Hello {guild.owner.name},\nYour server ``{guild.name}`` has been unbanned! Members can now use my commands again! This unban was issued by ``{banner_user['username']}``."),
                                loop
                            )
                            send_fut.result()
                            return "OK", 200
                        except discord.Forbidden as e:
                            getLogger().error(
                                f"Missing permission to send server unban notification to user {guild.owner} ({guild.owner.id})! Error: {e.text}")
                            return "missing permissions", 500
                        except discord.HTTPException as e:
                            getLogger().error(
                                f"Failed to send server unban notification to user {guild.owner} ({guild.owner.id})! Error: {e.text}")
                            return "failed", 500
                        except discord.InvalidArgument as e:
                            getLogger().error(
                                f"Failed to send server unban notification to user {guild.owner} ({guild.owner.id})! Error: {e}")
                            return "invalid argument, we shouldnt be here?!", 500
                    else:
                        return "Guild is none", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/banUserNotification", methods=["POST"])
def admin_ban_user_notify():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    user_id = int(request.get_json()["user_id"])
                    user = bot.get_user(user_id)
                    if user is not None:
                        reason = request.get_json()["reason"] if request.get_json()["reason"] != "" else "not specified"
                        try:
                            banner_user = discord_session.get("https://discordapp.com/api/users/@me").json()
                            send_fut = asyncio.run_coroutine_threadsafe(
                                user.send(
                                    f"Hello {user.name},\nYou have been banned and won't be able to use my commands! This ban was issued by ``{banner_user['username']}`` with reason: ``{reason}``."),
                                loop
                            )
                            send_fut.result()
                            return "OK", 200
                        except discord.Forbidden as e:
                            getLogger().error(
                                f"Missing permission to user server ban notification to user {user} ({user.id})! Error: {e.text}")
                            return "missing permissions", 500
                        except discord.HTTPException as e:
                            getLogger().error(
                                f"Failed to send user ban notification to user {user} ({user.id})! Error: {e.text}")
                            return "failed", 500
                        except discord.InvalidArgument as e:
                            getLogger().error(
                                f"Failed to send user ban notification to user {user} ({user.id})! Error: {e}")
                            return "invalid argument, we shouldnt be here?!", 500
                    else:
                        return "User is none", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/unbanUserNotification", methods=["POST"])
def admin_unban_user_notify():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    user_id = int(request.get_json()["user_id"])
                    user = bot.get_user(user_id)
                    if user is not None:
                        try:
                            banner_user = discord_session.get("https://discordapp.com/api/users/@me").json()
                            send_fut = asyncio.run_coroutine_threadsafe(
                                user.send(
                                    f"Hello {user.name},\nYou have been unbanned and can use my commands again! This unban was issued by ``{banner_user['username']}``."),
                                loop
                            )
                            send_fut.result()
                            return "OK", 200
                        except discord.Forbidden as e:
                            getLogger().error(
                                f"Missing permission to send user unban notification to user {user} ({user.id})! Error: {e.text}")
                            return "missing permissions", 500
                        except discord.HTTPException as e:
                            getLogger().error(
                                f"Failed to send user unban notification to user {user} ({user.id})! Error: {e.text}")
                            return "failed", 500
                        except discord.InvalidArgument as e:
                            getLogger().error(
                                f"Failed to send user unban notification to user {user} ({user.id})! Error: {e}")
                            return "invalid argument, we shouldnt be here?!", 500
                    else:
                        return "User is none", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/toggleModule", methods=["POST"])
def admin_toggle_module():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    module = request.get_json()["module"]
                    enabled = request.get_json()["enabled"]

                    old_json = json.loads(open("settings.json", 'r').read())
                    old_json["modules"][module] = enabled

                    with open("settings.json", 'w') as f:
                        f.write(json.dumps(old_json))
                        f.close()
                    return "Settings Updated", 200
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/modules", methods=["GET"])
def admin_modules():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                return jsonify(json.loads(open("settings.json", 'r').read()))
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


@app.route("/api/v1/server/<int:server_id>/modules")
def api_get_server_modules(server_id):
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                server = bot.get_guild(server_id)
                server_document = ServerSettings(server).getServerDocument()
                if server is not None:
                    return jsonify(server_document["modules"])
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


if __name__ == "__main__":
    SetupLogger()  # setup the logger with colored logger and verbose logging
    # Socket().run()  # create socketio instance

# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
