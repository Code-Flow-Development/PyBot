import calendar
import os
import json
from datetime import datetime
from config import getLogger
from dateutil.relativedelta import relativedelta
from discord.ext.commands import errors


def loadallcogs(bot):
    # loads cogs
    for command in os.listdir("cogs"):
        if command.endswith("py"):
            filename = command.split(".")[0]
            try:
                bot.load_extension(f"cogs.{filename}")
                getLogger().info(f"[Cog Management] Cog Loaded: {filename}")
            except (errors.ExtensionNotFound, errors.ExtensionAlreadyLoaded, errors.NoEntryPointError,
                    errors.ExtensionFailed) as e:
                getLogger().error(f"[Cog Management] Error loading cog: {filename} - {e}")


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


class UserProfile(int):
    def __init__(self, userid):
        self.userid = userid
        self.filename = f"data\\{self.userid}.json"

    def readUserProfile(self):
        file = open(self.filename, 'r')
        return json.loads(file.read())

    def save(self, content):
        file = open(self.filename, 'w')
        file.write(json.dumps(content))
