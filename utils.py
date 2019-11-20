import calendar
import os
import json
import discord
import random
from datetime import datetime
from config import getLogger, getMongoClient
from dateutil.relativedelta import relativedelta
from discord.ext.commands import errors


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
            "MiscData": {}
        }
        idd = self.user_collection.insert_one(user_payload).inserted_id
        getLogger().info(f"Inserted document for user '{member.name}' ({member.id}), ID: {idd}")

    def getUserProfile(self):
        profile = self.user_collection.find_one({"userid": self.member.id})
        return json.loads(profile)

    def save(self, updated_content):
        replace = self.user_collection.replace_one({"id": self.member.id}, json.dumps(updated_content))
        print(replace)



class UserProfile(discord.Member):
    def __init__(self, member):
        self.member = member
        self.filename = f"data\\{member.id}.json"
        if not member.bot:
            if not os.path.exists(self.filename):
                file = open(self.filename, 'w')
                json_payload = {
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
                file.write(json.dumps(json_payload))
                file.close()
                getLogger().info(f"Wrote new data file for user `{member.name} ({member.id})`")

    def readUserProfile(self):
        file = open(self.filename, 'r')
        return json.loads(file.read())

    def save(self, content):
        file = open(self.filename, 'w')
        file.write(json.dumps(content))


def getRandomFact():
    file = open("didyouknow.json", 'r')
    file_content = file.read()
    json_data = json.loads(file_content)
    return random.choice(json_data)
