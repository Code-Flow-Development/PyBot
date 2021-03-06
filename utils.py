import asyncio
import calendar
import json
import logging
import os
import random
from datetime import datetime
from functools import partial
from threading import Thread

import coloredlogs
import discord
import requests
import verboselogs
from async_timeout import timeout
from bson.json_util import dumps
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext.commands import errors
from dotenv import load_dotenv
from praw import Reddit
from profanityfilter import ProfanityFilter
from pymongo import MongoClient
from redis import Redis
from youtube_dl import YoutubeDL

load_dotenv()


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
        getLogger().debug(f"[MongoDB] Deleted user document for '{self.user.name}' ({self.user.id})")
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
                    "counting_channel": None,
                    "server_stats_category_id": None,
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
                        "guild_role_create": True,
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
                        "server_stats": False
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
                    ],
                    "profanity_filter_words": []
                }
            }
            self.server_collection.insert_one(guild_payload)
            getLogger().debug(f"[MongoDB] Created server document for '{guild.name}' ({guild.id})")
        self.server_settings = self.getServerSettings()

    def getServerSettings(self):
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

    def profanity_filter(self):
        return ProfanityFilter(extra_censor_list=self.server_settings["profanity_filter_words"])


def getRandomFact():
    facts_json_url = "https://gist.githubusercontent.com/Puyodead1/480702b0c64ea0bd6391a3ecc7cf9d79/raw/2a7010310f82fbc82edaf55134c57ccbdb7cead8/facts.json"
    res = requests.get(facts_json_url)
    if res.status_code == 200:
        return random.choice(res.json())
    else:
        return None


class LeagueAPI:
    def __init__(self):
        self.version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        self.champions_url = "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/championFull.json"
        self.runes_url = "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/runesReforged.json"
        self.items_url = "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/item.json"
        self.champion_url = "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion/{}.json"
        self.champion_avatar_url = "http://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}"
        self.item_image_url = "http://ddragon.leagueoflegends.com/cdn/{}/img/item/{}"

    def getCurrentVersion(self):
        response = requests.get(self.version_url)
        if response.status_code == 200:
            return response.json()[0]
        else:
            getLogger().error(
                f"[League of Legends] Version API call failed! Status Code: {response.status_code}; Response Text: {response.text}")
            return None

    def getChampions(self):
        '''
        JSON values:
        version, id, name, title, blurb, info, image, tags, partype, stats
        :return: JSON objector none if error
        '''
        current_version = self.getCurrentVersion()
        if current_version is not None:
            response = requests.get(self.champions_url.format(current_version))
            if response.status_code == 200:
                return response.json()
        else:
            getLogger().error(
                f"[League of Legends] Champion API call failed! current version is none! {current_version}")
            return None

    def getRunes(self):
        """
        JSON values:
        key, icon, name, slots

        slot values:
        runes: list

        slot -> runes values:
        id, key, icon, name, shotDesc, longDesc

        :return: list if json objects or None if error
        """
        current_version = self.getCurrentVersion()
        if current_version is not None:
            response = requests.get(self.runes_url.format(current_version))
            if response.status_code == 200:
                return response.json()
        else:
            return None

    def getItems(self):
        """
        JSON Values:
        name, description, plaintext, image, gold, tags, stats
        :return: JSON object of items or None if error
        """
        current_version = self.getCurrentVersion()
        if current_version is not None:
            response = requests.get(self.items_url.format(current_version))
            if response.status_code == 200:
                return response.json()
        else:
            return None

    def getChampion(self, champion):
        current_version = self.getCurrentVersion()
        if current_version is not None:
            response = requests.get(self.champion_url.format(current_version, champion))
            if response.status_code == 200:
                return response.json()
        else:
            return None

    def getChampionAvatarURL(self, champion):
        current_version = self.getCurrentVersion()
        if current_version is not None:
            response = requests.get(self.champion_url.format(current_version, champion))
            if response.status_code == 200:
                image_name = response.json()["data"][champion]["image"]["full"]
                url = self.champion_avatar_url.format(current_version, image_name)
                getLogger().debug(url)
                return url
        else:
            return None

    def getItem(self, item_id):
        current_version = self.getCurrentVersion()
        if current_version is not None:
            response = requests.get(self.items_url.format(current_version))
            if response.status_code == 200:
                return response.json()["data"][item_id]
        else:
            return None

    def getItemImage(self, item_id):
        current_version = self.getCurrentVersion()
        if current_version is not None:
            response = requests.get(self.items_url.format(current_version))
            if response.status_code == 200:
                image_name = response.json()["data"][item_id]["image"]["full"]
                return self.item_image_url.format(current_version, image_name)
        else:
            return None


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
    def __init__(self, full_debug=False):
        verboselogs.install()
        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level="DEBUG", logger=self.logger if not full_debug else None,
                            fmt="[%(levelname)s] %(asctime)s: %(message)s",
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


class RedisClient:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "127.0.0.1")
        self.port = os.getenv("REDIS_PORT", 6379)
        self.db = os.getenv("REDIS_DB", 0)
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.client = Redis(host=self.host, port=self.port, db=self.db, password=self.password)

    def getRedisClient(self):
        return self.client


def getSystemLogChannel(bot):
    return bot.get_channel(int(os.getenv("SYSTEM_LOG_CHANNEL_ID")))


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""
    pass


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""
    pass


class YTDL:
    def __init__(self):
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        self.ffmpeg_opts = {
            'before_options': '-nostdin',
            'options': '-vn'
        }
        self.ytdl = YoutubeDL(self.ytdl_opts)

    @property
    def get(self):
        return self.ytdl


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(YTDL().get.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if data["_type"] == "playlist":
            await ctx.send(f'```ini\n[Added {len(data["entries"])} songs to the Queue.]\n```', delete_after=15)
            a = []
            for entry in data["entries"]:
                a.append({'webpage_url': entry['webpage_url'], 'requester': ctx.author, 'title': entry["title"]})
            return a

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f'```ini\n[Added {data["title"]} to the Queue.]\n```', delete_after=15)

        if download:
            source = YTDL().get.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(YTDL().get.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                if self in self._cog.players.values():
                    return self.destroy(self._guild)
                return

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Converter:
    @classmethod
    def activity_type(cls, activity_type: str):
        return discord.ActivityType.watching if activity_type == "watching" else discord.ActivityType.listening if activity_type == "listening" else discord.ActivityType.playing if activity_type == "playing" else None

    @classmethod
    def activity_type_full(cls, member: discord.Member):
        current_activity_type = str(member.activity.type)
        return discord.ActivityType.watching if current_activity_type == "ActivityType.watching" else discord.ActivityType.listening if current_activity_type == "ActivityType.listening" else discord.ActivityType.playing if current_activity_type == "ActivityType.playing" else None

    @classmethod
    def status(cls, status: str):
        return discord.Status.dnd if status == "dnd" or status == "do_not_disturb" else discord.Status.idle if status == "idle" else discord.Status.online if status == "online" else discord.Status.offline if status == "offline" or status == "invisible" else None


class ServerStats:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.server_document = ServerSettings(guild)
        self.server_settings = self.server_document.getServerSettings()
        self.server_stats_enabled = self.server_settings["modules"]["server_stats"]

    def isEnabled(self):
        return self.server_stats_enabled

    async def enable(self):
        self.server_stats_enabled = True
        category = await self.guild.create_category("📊 Server Stats")
        await category.edit(position=0)
        await category.create_voice_channel(f"All Members {len(self.guild.members)}", overwrites={self.guild.default_role: discord.PermissionOverwrite(connect=False)})
        await category.create_voice_channel(f"Humans: {len([x for x in self.guild.members if not x.bot])}", overwrites={self.guild.default_role: discord.PermissionOverwrite(connect=False)})
        await category.create_voice_channel(f"Bots: {len([x for x in self.guild.members if x.bot])}", overwrites={self.guild.default_role: discord.PermissionOverwrite(connect=False)})
        await category.create_voice_channel(f"Channels: {len(self.guild.channels)}", overwrites={self.guild.default_role: discord.PermissionOverwrite(connect=False)})
        await category.create_voice_channel(f"Roles: {len(self.guild.roles)}", overwrites={self.guild.default_role: discord.PermissionOverwrite(connect=False)})

        self.server_settings["server_stats_category_id"] = category.id

        self.server_document.update("settings", self.server_settings)

    async def disable(self):
        self.server_stats_enabled = False
        category = self.guild.get_channel(self.server_settings["server_stats_category_id"])

        for channel in category.channels:
            await channel.delete()

        await category.delete()

        self.server_settings["server_stats_category_id"] = None

        self.server_document.update("settings", self.server_settings)

    async def update(self):
        category = self.guild.get_channel(self.server_settings["server_stats_category_id"])
        for channel in category.channels:
            if channel.name.startswith("All Members"):
                await channel.edit(name=f"All Members {len(self.guild.members)}")
            elif channel.name.startswith("Humans"):
                await channel.edit(name=f"Humans: {len([x for x in self.guild.members if not x.bot])}")
            elif channel.name.startswith("Bots"):
                await channel.edit(name=f"Bots: {len([x for x in self.guild.members if x.bot])}")
            elif channel.name.startswith("Channels"):
                await channel.edit(name=f"Channels: {len(self.guild.channels)}")
            elif channel.name.startswith("Roles"):
                await channel.edit(name=f"Roles: {len(self.guild.roles)}")
