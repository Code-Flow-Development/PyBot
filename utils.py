import calendar
import os
import json
import discord
import random
from datetime import datetime
from config import getLogger, getMongoClient
from dateutil.relativedelta import relativedelta
from discord.ext.commands import errors
from bson.json_util import dumps


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
                getLogger().error(f"[Cog Management] Error loading cog: {filename} - {e}")


def loadAllExtensions(bot):
    for extension in os.listdir("extensions"):
        if extension.endswith("py"):
            file = extension.split(".")[0]
            try:
                bot.load_extension(f"extensions.{file}")
                getLogger().info(f"[Extension Management] Extension Loaded: {file}")
            except (errors.ExtensionNotFound, errors.ExtensionAlreadyLoaded, errors.NoEntryPointError,
                    errors.ExtensionFailed) as e:
                getLogger().error(f"[Extension Management] Error loading extension: {file} - {e}")


def utc_to_epoch(utc: datetime):
    return calendar.timegm(utc.utctimetuple())


class EpochUtils(float):
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


class UserProfiles(discord.Member):
    def __init__(self, member):
        mongoclient = getMongoClient()
        self.db = mongoclient["PyBot"]
        self.user_collection = self.db["users"]
        self.member = member

        user = self.user_collection.find_one({"id": member.id})
        if not user:
            user_payload = {
                "id": member.id,
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
                    "strikes": []
                }
            }
            idd = self.user_collection.insert_one(user_payload).inserted_id
            getLogger().debug(f"[MongoDB] Created user document for '{member.name}' ({member.id}), Document ID: {idd}")

    def getUserProfile(self):
        profile = self.user_collection.find_one({"id": self.member.id})
        return json.loads(dumps(profile))

    def update(self, key, value):
        self.user_collection.update_one({"id": self.member.id}, {"$set": {key: value}})

    def reset(self):
        result = self.user_collection.delete_one({"id": self.member.id})
        return result


class ServerSettings(discord.Guild):
    def __init__(self, guild):
        self.guild = guild
        mongoclient = getMongoClient()
        self.db = mongoclient["PyBot"]
        self.server_collection = self.db["servers"]

        server = self.server_collection.find_one({"id": guild.id})
        if not server:
            guild_payload = {
                "id": guild.id,
                "name": guild.name,
                "settings": {
                    "log_channel": None,
                    "message_responses_enabled": False,
                    "counting_channels_enabled": False,
                    "events": {
                        "guild_member_join": True,
                        "guild_member_leave": True,
                        "guild_member_update": True,
                        "guild_member_ban": True,
                        "guild_member_unban": True,
                        "guild_update": True,
                        "guild_message_delete": True,
                        "guild_message_edit": True,
                        "guild_channel_delete": True,
                        "guild_channel_create": True,
                        "guild_channel_update": True,
                        "guild_role_created": True,
                        "guild_role_delete": True,
                        "guild_role_update": True,
                        "guild_emojis_update": True,
                        "user_update": True
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
            idd = self.server_collection.insert_one(guild_payload).inserted_id
            getLogger().debug(f"[MongoDB] Created server document for '{guild.name}' ({guild.id}), Document ID: {idd}")
        self.server_settings = self.getServerDocument()

    def getServerDocument(self):
        document = self.server_collection.find_one({"id": self.guild.id})
        return json.loads(dumps(document))["settings"]

    def update(self, key, value):
        self.server_collection.update_one({"id": self.guild.id}, {"$set": {key: value}})

    def reset(self):
        result = self.server_collection.delete_one({"id": self.guild.id})
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
    contents = open("LoLData\\LoLBoots.json", 'r').read()
    return json.loads(contents)


def getLoLChampsJson():
    contents = open("LoLData\\LoLChamps.json", 'r').read()
    return json.loads(contents)


def getLoLItemsJson():
    contents = open("LoLData\\LoLItems.json", 'r').read()
    return json.loads(contents)


def getLoLjgItemsJson():
    contents = open("LoLData\\LoLjgItems.json", 'r').read()
    return json.loads(contents)


def getLoLRunesJson():
    contents = open("LoLData\\LoLRunes.json", 'r').read()
    return json.loads(contents)


def getLoLSuppItemsJson():
    contents = open("LoLData\\LoLsuppItems.json", 'r').read()
    return json.loads(contents)


def getLoLChampsList():
    champs_json = getLoLChampsJson()
    for x in champs_json:
        return [a for a in x]
