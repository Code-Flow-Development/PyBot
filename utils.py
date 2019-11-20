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
        print(user)
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
                    "Inventory": {},
                },
                "MiscData": {
                    "strikes": []
                }
            }
            idd = self.user_collection.insert_one(user_payload).inserted_id
            getLogger().info(f"Inserted document for user '{member.name}' ({member.id}), ID: {idd}")

    def getUserProfile(self):
        profile = self.user_collection.find_one({"id": self.member.id})
        return json.loads(dumps(profile))

    def update(self, key, value):
        self.user_collection.update_one({"id": self.member.id}, {"$set": {key: value}})


def getRandomFact():
    file = open("didyouknow.json", 'r')
    file_content = file.read()
    json_data = json.loads(file_content)
    return random.choice(json_data)
