import asyncio
import calendar
import json
import logging
import os
import random
from datetime import datetime
from threading import Thread
import coloredlogs
import discord
import verboselogs
import youtube_dl
from bson.json_util import dumps
from flask_socketio import SocketIO, emit
from dateutil.relativedelta import relativedelta
from discord.ext.commands import errors
from praw import Reddit
from pymongo import MongoClient
from redis import Redis

from dotenv import load_dotenv

load_dotenv()

true = True
false = False


def loadAllCogs(bot):
    # loads cogs
    for cog in os.listdir("cogs"):
        if cog.endswith("py"):
            filename = cog.split(".")[0]
            try:
                bot.load_extension(f"cogs.{filename}")
                getLogger().info(f"[Cog Management] Cog Loaded: {filename}")
            except (errors.ExtensionNotFound, errors.ExtensionAlreadyLoaded, errors.NoEntryPointError,
                    errors.ExtensionFailed) as e:
                getLogger().error(f"[Cog Management] Error loading cog: {filename}; Error: {e}")


def loadAllExtensions(bot):
    for extension in os.listdir("extensions"):
        if extension.endswith("py"):
            file = extension.split(".")[0]
            try:
                bot.load_extension(f"extensions.{file}")
                getLogger().info(f"[Extension Management] Extension Loaded: {file}")
            except (errors.ExtensionNotFound, errors.ExtensionAlreadyLoaded, errors.NoEntryPointError,
                    errors.ExtensionFailed) as e:
                getLogger().error(f"[Extension Management] Error loading extension: {file}; Error: {e}")


def utc_to_epoch(utc: datetime):
    return calendar.timegm(utc.utctimetuple())


class EpochUtils:
    def __init__(self, unix):
        self.rdelta = relativedelta(datetime.now(), datetime.fromtimestamp(unix))

    def seconds(self):
        return self.rdelta.seconds

    def minutes(self):
        return self.rdelta.minutes

    def hours(self):
        return self.rdelta.hours

    def days(self):
        return self.rdelta.days

    def months(self):
        return self.rdelta.months

    def years(self):
        return self.rdelta.years


class UserProfiles:
    def __init__(self, user):
        mongoclient = Mongo().getMongoClient()
        self.db = mongoclient["PyBot"]
        self.user_collection = self.db["users"]
        self.user = user

        user_document = self.user_collection.find_one({"id": user.id})
        if not user_document:
            user_payload = {
                "id": user.id,
                "RPGData": {
                    "CreatedCharacter": False,
                    "Name": {
                        "FirstName": "none",
                        "MiddleName": "none",
                        "LastName": "none",
                    },
                    "Race": "none",
                    "Stats": {
                        "Level": 1,
                        "CurrentExp": 0,
                        "MaxExp": 100,
                        "Sheckels": 10,
                    },
                    "Inventory": [],
                },
                "MiscData": {
                    "strikes": [],
                    "is_banned": False
                }
            }
            self.user_collection.insert_one(user_payload)
            getLogger().debug(f"[MongoDB] Created user document for '{user.name}' ({user.id})")

    def getUserProfile(self):
        profile = self.user_collection.find_one({"id": self.user.id})
        return json.loads(dumps(profile))

    def update(self, key, value):
        self.user_collection.update_one({"id": self.user.id}, {"$set": {key: value}})

    def reset(self):
        result = self.user_collection.delete_one({"id": self.user.id})
        getLogger().debug(f"[MongoDB] Created user document for '{self.user.name}' ({self.user.id})")
        return result


class ServerSettings:
    def __init__(self, guild):
        self.guild = guild
        mongoclient = Mongo().getMongoClient()
        self.db = mongoclient["PyBot"]
        self.server_collection = self.db["servers"]

        server = self.server_collection.find_one({"id": guild.id})
        if not server:
            guild_payload = {
                "id": guild.id,
                "name": guild.name,
                "settings": {
                    "is_banned": False,
                    "log_channel": None,
                    "starboard_channel": None,
                    "events": {
                        "guild_member_join": True,
                        "guild_member_leave": True,
                        "guild_member_update": False,
                        "guild_member_ban": True,
                        "guild_member_unban": True,
                        "guild_update": False,
                        "guild_message_delete": True,
                        "guild_message_edit": False,
                        "guild_channel_delete": True,
                        "guild_channel_create": True,
                        "guild_channel_update": False,
                        "guild_role_created": True,
                        "guild_role_delete": True,
                        "guild_role_update": False,
                        "guild_emojis_update": False
                    },
                    "modules": {
                        "message_responses": False,
                        "counting_channels": False,
                        "music": False,
                        "lol": False,
                        "nsfw": False,
                        "starboard": False,
                        "profanity_filter": False,
                    },
                    "custom_message_responses": [
                        {
                            "trigger": "xd",
                            "response": "Ecks Dee"
                        },
                        {
                            "trigger": "meme",
                            "response": "shit meme"
                        }
                    ]
                }
            }
            self.server_collection.insert_one(guild_payload)
            getLogger().debug(f"[MongoDB] Created server document for '{guild.name}' ({guild.id})")
        self.server_settings = self.getServerDocument()

    def getServerDocument(self):
        document = self.server_collection.find_one({"id": self.guild.id})
        return json.loads(dumps(document))["settings"]

    def update(self, key, value):
        self.server_collection.update_one({"id": self.guild.id}, {"$set": {key: value}})

    def reset(self):
        result = self.server_collection.delete_one({"id": self.guild.id})
        getLogger().debug(f"[MongoDB] Reset server document for '{self.guild.name}' ({self.guild.id})")
        return result

    def getLogChannel(self, bot: discord.ext.commands.Bot):
        return bot.get_channel(self.server_settings["log_channel"]) if self.server_settings[
            "log_channel"] else None


def getRandomFact():
    file = open("didyouknow.json", 'r')
    file_content = file.read()
    json_data = json.loads(file_content)
    return random.choice(json_data)


def getLoLBootsJson():
    contents = open("LoLData\\LoLBoots.json", 'r', encoding='utf8').read()
    return json.loads(contents)


def getLoLChampsJson():
    contents = open("LoLData\\LoLChamps.json", 'r', encoding='utf8').read()
    return json.loads(contents)


def getLoLItemsJson():
    contents = open("LoLData\\LoLItems.json", 'r', encoding='utf8').read()
    return json.loads(contents)


def getLoLjgItemsJson():
    contents = open("LoLData\\LoLjgItems.json", 'r', encoding='utf8').read()
    return json.loads(contents)


def getLoLRunesJson():
    contents = open("LoLData\\LoLRunes.json", 'r', encoding='utf8').read()
    return json.loads(contents)


def getLoLSuppItemsJson():
    contents = open("LoLData\\LoLsuppItems.json", 'r', encoding='utf8').read()
    return json.loads(contents)


def getLoLChampsKeyList():
    champs_json = getLoLChampsJson()
    keys = []
    for x in champs_json:
        for key in x:
            keys.append(key)
    return keys


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, filename, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")
        self.filename = filename

    @classmethod
    async def from_url_play(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: YoutubeDL().getPlay().extract_info(url, download=True))

        if "entries" in data:
            data = data["entries"][0]

        filename = YoutubeDL().getPlay().prepare_filename(data)
        if os.path.exists(filename):
            return cls(discord.FFmpegPCMAudio(filename, **{"options": "-vn"}), filename=filename, data=data)
        else:
            return None

    @classmethod
    async def from_url_stream(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: YoutubeDL().getStream().extract_info(url, download=False))

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"]
        return cls(discord.FFmpegPCMAudio(filename, **{"options": "-vn"}), filename=filename, data=data)

    @classmethod
    def cleanup_file(cls, filename):
        os.remove(filename)


class Mongo:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))

    def getMongoClient(self):
        return self.client


class RedditClient:
    def __init__(self):
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USERAGENT")
        self.client = Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

    def getRedditClient(self):
        return self.client


class APIServer:
    def __init__(self, partial):
        self.FLASK_THREAD: Thread = Thread(target=partial, daemon=True)

    def getThread(self):
        return self.FLASK_THREAD

    def start(self):
        self.FLASK_THREAD.start()

    def stop(self):
        self.FLASK_THREAD.join()


class SetupLogger:
    def __init__(self):
        verboselogs.install()
        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level="DEBUG", logger=self.logger, fmt="[%(levelname)s] %(asctime)s: %(message)s",
                            datefmt="[%m-%d-%Y %I:%M:%S]")


def getLogger():
    return logging.getLogger(__name__)


class BotAdmins:
    def __init__(self):
        pass

    def get(self):
        return json.loads(open("settings.json", 'r').read())["admins"]

    def add(self, user_id: int):
        admins = json.loads(open("settings.json", 'r').read())
        try:
            if user_id not in admins["admins"]:
                admins["admins"].append(user_id)
                open("settings.json", 'w').write(json.dumps(admins))
                return True
            else:
                return False
        except ValueError:
            return False

    def remove(self, user_id: int):
        admins = json.loads(open("settings.json", 'r').read())
        try:
            admins["admins"].remove(user_id)
            open("settings.json", 'w').write(json.dumps(admins))
            return True
        except ValueError:
            return False


class YoutubeDL:
    def __init__(self):
        youtube_dl.utils.bug_reports_message = lambda: ''
        self.play_config = {
            "format": "bestaudio/best",
            "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "restrictfilenames": True,
            "noplaylist": True,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            "source_address": "0.0.0.0",
            "max_filesize": 100000000,  # 50 megabytes
            "age_limit": 13
        }
        self.stream_config = {
            "format": "bestaudio/best",
            "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "restrictfilenames": True,
            "noplaylist": False,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            "source_address": "0.0.0.0",
            "age_limit": 13
        }

        self.play = youtube_dl.YoutubeDL(self.play_config)
        self.stream = youtube_dl.YoutubeDL(self.stream_config)

    def getPlay(self):
        return self.play

    def getStream(self):
        return self.stream


class RedisClient:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "127.0.0.1")
        self.port = os.getenv("REDIS_PORT", 6379)
        self.db = os.getenv("REDIS_DB", 0)
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.client = Redis(host=self.host, port=self.port, db=self.db, password=self.password)

    def getRedisClient(self):
        return self.client


# class Socket:
#     def __init__(self):
#         self.app = web.Application()
#         self.client = socketio.AsyncServer(async_mode='aiohttp')
#         self.client.attach(self.app)
#         self.thread: Thread = Thread(target=web.run_app(self.app), daemon=True)
#
#         @self.client.event
#         def connect(sid, environ):
#             print('connect ', sid)
#
#         @self.client.event
#         def disconnect(sid):
#             print('disconnect ', sid)
#
#     def getClient(self):
#         return self.client
#
#     def run(self):
#         self.thread.start()


def getSystemLogChannel(bot):
    return bot.get_channel(int(os.getenv("SYSTEM_LOG_CHANNEL_ID")))
