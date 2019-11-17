import os
import discord
import calendar
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from discord.ext.commands import errors


def loadallcogs(bot):
    # loads cogs
    for command in os.listdir("cogs"):
        if command.endswith("py"):
            filename = command.split(".")[0]
            try:
                bot.load_extension(f"cogs.{filename}")
                logging.info(f"[Cog Management] Cog Loaded: {filename}")
            except (errors.ExtensionNotFound, errors.ExtensionAlreadyLoaded, errors.NoEntryPointError,
                    errors.ExtensionFailed) as e:
                logging.error(f"[Cog Management] Error loading cog: {filename} - {e}")


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
