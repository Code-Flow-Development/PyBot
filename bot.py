import asyncio
import json
import os
import time
from datetime import datetime
from functools import partial
from threading import Thread

import discord
from bson.json_util import dumps
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask, jsonify, session, request
from flask_session import Session
from requests_oauthlib import OAuth2Session

from utils import loadAllCogs, loadAllExtensions, SetupLogger, RedisClient, Mongo, APIServer, ServerSettings, getLogger, \
    UserProfiles, BotAdmins, getSystemLogChannel, Converter, ServerStats

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
bot = commands.Bot(command_prefix=PREFIX, description="PyBot", case_insensitive=True, owner_id=213247101314924545)
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

    await bot.change_presence(activity=discord.Activity(name=str(len(bot.users)) + " users!", type=discord.ActivityType.watching))

    # await bot.change_presence(activity=discord.Activity(name="hentai! 😳", type=discord.ActivityType.watching),
    #                           status=discord.Status.dnd)

    # Load cogs
    loadAllCogs(bot)

    # load extensions
    loadAllExtensions(bot)

    # Start the flask api
    partial_run = partial(app.run, debug=True, host=os.getenv("API_HOST"), port=os.getenv("API_PORT"),
                          use_reloader=False)
    APIServer(partial_run).start()

    # Create server documents for each server
    thread = Thread(target=worker, daemon=True)
    thread.start()

    if len(bot.guilds) >= 1000:
        getLogger().info("There are 1000+ guilds! If you aren't already, you should setup sharding!")


# message event
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.type == discord.ChannelType.private:
        spy_channel = bot.get_channel(652314012771549185)
        if len(message.content) > 0:
            embed = discord.Embed(title=f"{message.author.name} sent me a DM", description=message.content,
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.set_footer(text=f"Sent by {message.author}", icon_url=message.author.avatar_url)
            return await spy_channel.send(content=None, embed=embed)
        elif len(message.attachments) > 0:
            links = "\n".join([x.url for x in message.attachments])
            return await spy_channel.send(content=f"``{message.author}`` sent me a DM with attachments:\n{links}")

    user_profile = UserProfiles(message.author).getUserProfile()
    server_settings = ServerSettings(message.guild)
    server_document = server_settings.getServerSettings()
    if message.content.startswith(PREFIX):
        if not server_document["is_banned"] and not user_profile["MiscData"]["is_banned"]:
            await bot.process_commands(message)
    else:

        if message.channel.type == discord.ChannelType.text and message.channel.name.lower().startswith(
                "count-to-"):
            if server_document["modules"]["counting_channels"]:
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

        if server_document["modules"]["message_responses"]:
            custom_message_responses = server_document["custom_message_responses"]
            for custom_response in custom_message_responses:
                trigger = custom_response["trigger"]
                response = custom_response["response"]
                if trigger in message.content.lower():
                    await message.channel.send(response)
                    return

        # profanity filter
        if server_document["modules"]["profanity_filter"]:
            if server_settings.profanity_filter().is_profane(message.content):
                await message.delete()
                await message.channel.send("Watch your language! :rage:", delete_after=10)


@app.route("/api/v1/userCount", methods=["GET"])
def api_user_count():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                return jsonify({"user_count": len(bot.users)}), 200
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


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
                    try:
                        users.append({"username": x.name, "id": x.id, "discriminator": x.discriminator,
                                      "avatar_url": str(x.avatar_url),
                                      "is_banned": user_json["MiscData"]["is_banned"],
                                      "is_admin": user["id"] in BotAdmins().get()})
                    except AttributeError as e:
                        getLogger().critical(f"[Users API]: User Error - ID: {user['id']}")
                        user_collection.find_one_and_delete({"id": user['id']})
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


@app.route("/api/v1/admin/bot", methods=["GET"])
def api_bot():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                member = bot.get_guild(644927766197698590).get_member(bot.user.id)
                bot_info = {
                    "latency": bot.latency,
                    "user": {
                        "id": bot.user.id,
                        "name": str(bot.user),
                        "avatar_url": str(bot.user.avatar_url)
                    },
                    "activity": {
                        "name": str(member.activity.name),
                        "type": str(member.activity.type)
                    },
                    "status": str(member.status),
                    "servers": len(bot.guilds),
                    "users": len(bot.users),
                    "voice_clients": len(bot.voice_clients),
                    "shards": bot.shard_count
                }
                return jsonify(bot_info)
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

                            send_fut2 = asyncio.run_coroutine_threadsafe(
                                getSystemLogChannel(bot).send(
                                    f"{guild.name} ({guild.id}) was banned by ``{banner_user['username']}``."),
                                loop
                            )
                            send_fut2.result()
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

                            send_fut2 = asyncio.run_coroutine_threadsafe(
                                getSystemLogChannel(bot).send(
                                    f"{guild.name} ({guild.id}) was unbanned by ``{banner_user['username']}``."),
                                loop
                            )
                            send_fut2.result()
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

                            send_fut2 = asyncio.run_coroutine_threadsafe(
                                getSystemLogChannel(bot).send(
                                    f"[{user.mention}] {user} ({user.id}) was banned by ``{banner_user['username']}`` with reason: ``{reason}``."),
                                loop
                            )
                            send_fut2.result()
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

                            send_fut2 = asyncio.run_coroutine_threadsafe(
                                getSystemLogChannel(bot).send(
                                    f"[{user.mention}] {user} ({user.id}) was unbanned by ``{banner_user['username']}``."),
                                loop
                            )
                            send_fut2.result()
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
                    old_json["modules"][module]["enabled"] = enabled

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
                return jsonify(json.loads(open("settings.json", 'r').read())["modules"])
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/server/<int:server_id>", methods=["GET"])
def api_get_server(server_id):
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                server = bot.get_guild(server_id)
                server_settings = ServerSettings(server).getServerSettings()
                if server is not None:
                    return jsonify(
                        {"name": server.name, "id": server.id, "region": server.region.name,
                         "icon_url": str(server.icon_url),
                         "voice_channel_amount": len(server.voice_channels),
                         "text_channel_amount": len(server.text_channels),
                         "category_amount": len(server.categories), "member_count": server.member_count,
                         "role_amount": len(server.roles),
                         "text_channels": [{"name": y.name, "id": y.id} for y in server.text_channels],
                         "roles": [{"name": z.name, "id": z.id} for z in server.roles if z.name != "@everyone"],
                         "log_channel": server_settings["log_channel"], "is_banned": server_settings["is_banned"],
                         "events": server_settings["events"], "modules": server_settings["modules"],
                         "counting_channel": server_settings["counting_channel"]})
                else:
                    return "", 400
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/modules", methods=["GET"])
def api_get_modules():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                return jsonify(json.loads(open("settings.json", 'r').read())["modules"])
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/events", methods=["GET"])
def api_get_events():
    if bot.is_ready():
        token = request.headers.get("Token")
        if token is not None:
            token = json.loads(token)
            discord_session = make_session(token=token)
            if discord_session.authorized:
                return jsonify(json.loads(open("settings.json", 'r').read())["events"])
            else:
                return "", 401
        else:
            return "", 403
    else:
        return "bot is not ready!", 500


@app.route("/api/v1/user/<int:user_id>", methods=["GET"])
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


@app.route("/api/v1/admin/promoteUser", methods=["POST"])
def admin_promote_user():
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
                        BotAdmins().add(user_id)
                        try:
                            promoter = discord_session.get("https://discordapp.com/api/users/@me").json()
                            promoter_user = bot.get_user(int(promoter['id']))

                            user_embed = discord.Embed(title="You have been promoted to an Admin of mine!",
                                                       description=f"You will now have access to the admin panel of the dashboard and bot admin commands!\nThis promotion was issued by ``{promoter['username']}``.",
                                                       color=discord.Color.green(),
                                                       timestamp=datetime.utcnow())
                            user_embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

                            send_fut = asyncio.run_coroutine_threadsafe(
                                user.send(content=None, embed=user_embed),
                                loop
                            )
                            send_fut.result()

                            log_embed = discord.Embed(title="New Bot Admin",
                                                      description=f"{user.mention} was added as a bot admin by {promoter_user.mention}",
                                                      color=discord.Color.green(),
                                                      timestamp=datetime.utcnow())
                            log_embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
                            # embed.set_footer(text=author.name, icon_url=author.avatar_url)

                            send_fut2 = asyncio.run_coroutine_threadsafe(
                                getSystemLogChannel(bot).send(content=None, embed=log_embed),
                                loop
                            )
                            send_fut2.result()
                            return "OK", 200
                        except discord.Forbidden as e:
                            getLogger().error(
                                f"Missing permission to send promotion notification to user {user} ({user.id})! Error: {e.text}")
                            return "missing permissions", 500
                        except discord.HTTPException as e:
                            getLogger().error(
                                f"Failed to send promotion notification to user {user} ({user.id})! Error: {e.text}")
                            return "failed", 500
                        except discord.InvalidArgument as e:
                            getLogger().error(
                                f"Failed to send promotion notification to user {user} ({user.id})! Error: {e}")
                            return "invalid argument, we shouldnt be here?!", 500
                    else:
                        return "user is none", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/demoteUser", methods=["POST"])
def admin_demote_user():
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
                        BotAdmins().remove(user_id)
                        try:
                            demoter = discord_session.get("https://discordapp.com/api/users/@me").json()
                            demoter_user = bot.get_user(int(demoter['id']))

                            user_embed = discord.Embed(title="You have been demoted from an Admin of mine!",
                                                       description=f"You will no longer have access to the admin panel of the dashboard and bot admin commands!\nThis demotion was issued by ``{demoter['username']}``.",
                                                       color=discord.Color.red(),
                                                       timestamp=datetime.utcnow())
                            user_embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

                            send_fut = asyncio.run_coroutine_threadsafe(
                                user.send(content=None, embed=user_embed),
                                loop
                            )
                            send_fut.result()

                            log_embed = discord.Embed(title="Bot Admin Removed",
                                                      description=f"{user.mention} was removed as a bot admin by {demoter_user.mention}",
                                                      color=discord.Color.red(),
                                                      timestamp=datetime.utcnow())
                            log_embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
                            # embed.set_footer(text=author.name, icon_url=author.avatar_url)

                            send_fut2 = asyncio.run_coroutine_threadsafe(
                                getSystemLogChannel(bot).send(content=None, embed=log_embed),
                                loop
                            )
                            send_fut2.result()
                            return "OK", 200
                        except discord.Forbidden as e:
                            getLogger().error(
                                f"Missing permission to send demotion notification to user {user} ({user.id})! Error: {e.text}")
                            return "missing permissions", 500
                        except discord.HTTPException as e:
                            getLogger().error(
                                f"Failed to send demotion notification to user {user} ({user.id})! Error: {e.text}")
                            return "failed", 500
                        except discord.InvalidArgument as e:
                            getLogger().error(
                                f"Failed to send demotion notification to user {user} ({user.id})! Error: {e}")
                            return "invalid argument, we shouldnt be here?!", 500
                    else:
                        return "user is none", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/bot/changeAvatar", methods=["POST"])
def admin_bot_change_avatar():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    path = request.json.get("path")
                    if path and path is not None and path != "":
                        with open(path, 'rb') as image:
                            try:
                                leave_fut = asyncio.run_coroutine_threadsafe(
                                    bot.user.edit(avatar=image.read()),
                                    loop
                                )
                                leave_fut.result()
                                image.close()
                                return "Avatar was changed", 200
                            except discord.HTTPException:
                                return "Failed to edit profile", 500
                            except discord.InvalidArgument:
                                return "Wrong image format passed for avatar", 400
                            except discord.ClientException:
                                return "Password is required for non-bot accounts or house field was not a valid HypeSquad house", 400
                    else:
                        return "", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/<int:server_id>/toggleModule", methods=["POST"])
def server_toggle_module(server_id):
    if request.is_json:
        if server_id is not None and server_id != "":
            if bot.is_ready():
                token = request.headers.get("Token")
                if token is not None:
                    token = json.loads(token)
                    discord_session = make_session(token=token)
                    if discord_session.authorized:
                        server = bot.get_guild(server_id)
                        if server is not None:
                            user = discord_session.get("https://discordapp.com/api/users/@me").json()
                            module = request.get_json()["module"]
                            enabled = bool(request.get_json()["enabled"])
                            smart_action = bool(request.get_json()["smart_action"])

                            server_document = ServerSettings(server)
                            server_settings = server_document.getServerSettings()
                            server_settings["modules"][module] = enabled
                            server_document.update("settings", server_settings)

                            if module.lower() == "counting_channels":
                                # use this to delete current counting channel if exists or create a new one
                                if enabled and smart_action is not None and smart_action:
                                    # create
                                    counting_channel = server_settings["counting_channel"]
                                    if counting_channel is None:
                                        try:
                                            create_fut = asyncio.run_coroutine_threadsafe(
                                                server.create_text_channel(name="count-to-1",
                                                                           reason=f"Module enabled via dashboard by {user['username']}"),
                                                loop
                                            )
                                            channel = create_fut.result()
                                            server_settings["counting_channel"] = channel.id
                                            server_document.update("settings", server_settings)
                                        except discord.Forbidden as e:
                                            pass
                                        except discord.HTTPException as e:
                                            pass
                                        except discord.InvalidArgument as e:
                                            pass
                                elif not enabled and smart_action is not None and smart_action:
                                    # delete
                                    try:
                                        channel = server.get_channel(server_settings["counting_channel"])
                                        delete_fut = asyncio.run_coroutine_threadsafe(
                                            channel.delete(
                                                reason=f"Module disabled via dashboard by {user['username']}"),
                                            loop
                                        )
                                        delete_fut.result()
                                        server_settings["counting_channel"] = None
                                        server_document.update("settings", server_settings)
                                    except discord.Forbidden:
                                        pass
                                    except discord.NotFound:
                                        pass
                                    except discord.HTTPException:
                                        pass
                            elif module.lower() == "server_stats":
                                if enabled:
                                    enable_fut = asyncio.run_coroutine_threadsafe(
                                        ServerStats(bot, server).enable(),
                                        loop
                                    )
                                    enable_fut.result()
                                else:
                                    disable_fut = asyncio.run_coroutine_threadsafe(
                                        ServerStats(bot, server).disable(),
                                        loop
                                    )
                                    disable_fut.result()
                            return "Settings Updated", 200
                        else:
                            return "", 400
                    else:
                        return "", 401
                else:
                    return "", 403
            else:
                return "bot is not ready!", 500
        else:
            return "", 400
    else:
        return "", 400


@app.route("/api/v1/admin/bot/setActivityName", methods=["POST"])
def admin_bot_set_activity_name():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    new_activity_name = request.get_json()["new_activity_name"]
                    try:
                        member = bot.get_guild(644927766197698590).get_member(bot.user.id)
                        leave_fut = asyncio.run_coroutine_threadsafe(
                            bot.change_presence(activity=discord.Activity(name=new_activity_name,
                                                                          type=discord.ActivityType.watching if str(
                                                                              member.activity.type) == "ActivityType.watching" else discord.ActivityType.listening if str(
                                                                              member.activity.type) == "ActivityType.listening" else discord.ActivityType.playing),
                                                status=member.status),
                            loop
                        )
                        leave_fut.result()
                        return "Activity Name was changed", 200
                    except discord.HTTPException:
                        return "Failed to edit profile", 500
                    except discord.InvalidArgument:
                        return "Wrong image format passed for avatar", 400
                    except discord.ClientException:
                        return "Password is required for non-bot accounts or house field was not a valid HypeSquad " \
                               "house", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/bot/setActivityType", methods=["POST"])
def admin_bot_set_activity_type():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    new_activity_type = request.get_json()["new_activity_type"]
                    try:
                        member = bot.get_guild(644927766197698590).get_member(bot.user.id)
                        leave_fut = asyncio.run_coroutine_threadsafe(
                            bot.change_presence(activity=discord.Activity(name=member.activity.name,
                                                                          type=discord.ActivityType.watching if new_activity_type == "watching" else discord.ActivityType.listening if new_activity_type == "listening" else discord.ActivityType.playing),
                                                status=member.status),
                            loop
                        )
                        leave_fut.result()
                        return "Activity Type was changed", 200
                    except discord.HTTPException:
                        return "Failed to edit profile", 500
                    except discord.InvalidArgument:
                        return "Wrong image format passed for avatar", 400
                    except discord.ClientException:
                        return "Password is required for non-bot accounts or house field was not a valid HypeSquad " \
                               "house", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


@app.route("/api/v1/admin/bot/setStatus", methods=["POST"])
def admin_bot_set_status():
    if request.is_json:
        if bot.is_ready():
            token = request.headers.get("Token")
            if token is not None:
                token = json.loads(token)
                discord_session = make_session(token=token)
                if discord_session.authorized:
                    new_status = request.get_json()["new_status"]
                    try:
                        member = bot.get_guild(644927766197698590).get_member(bot.user.id)
                        leave_fut = asyncio.run_coroutine_threadsafe(bot.change_presence(activity=discord.Activity(name=member.activity.name, type=Converter.activity_type_full(member)), status=Converter.status(new_status)), loop)
                        leave_fut.result()
                        return "Status was changed", 200
                    except discord.HTTPException:
                        return "Failed to edit profile", 500
                    except discord.InvalidArgument:
                        return "Wrong image format passed for avatar", 400
                    except discord.ClientException:
                        return "Password is required for non-bot accounts or house field was not a valid HypeSquad " \
                               "house", 400
                else:
                    return "", 401
            else:
                return "", 403
        else:
            return "bot is not ready!", 500
    else:
        return "", 400


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
    # setup the logger with colored logger and verbose logging
    SetupLogger(full_debug=False)

# login to discord
bot.run(os.getenv("TOKEN"))
