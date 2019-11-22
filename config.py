import coloredlogs
import logging
import verboselogs
import json
import discord
from pymongo import MongoClient

PREFIX = "{"
BOT_LOG_CHANNEL_ID = 647218189218086937


def getBotLogChannel(bot: discord.ext.commands.Bot):
    return bot.get_channel(BOT_LOG_CHANNEL_ID)


def getBotAdmins():
    file = open("admins.json", 'r')
    contents = file.read()
    return json.loads(contents)


def addBotAdmin(user_id: int):
    file = open("admins.json", 'r+')
    current_admins = json.loads(file.read())
    file.truncate(0)
    file.close()
    current_admins.append(user_id)
    file = open("admins.json", 'w')
    file.write(json.dumps(current_admins))


def removeBotAdmin(user_id: int):
    file = open("admins.json", 'r+')
    current_admins = json.loads(file.read())
    file.truncate(0)
    file.close()
    current_admins.remove(user_id)
    file = open("admins.json", 'w')
    file.write(json.dumps(current_admins))


def getLogger():
    verboselogs.install()
    logger = logging.getLogger("PyBot")
    coloredlogs.install(level="DEBUG", logger=logger, fmt="[%(levelname)s] %(asctime)s: %(message)s",
                        datefmt="[%m-%d-%Y %I:%M:%S]")
    return logger


def getMongoClient():
    return MongoClient('mongodb://185.230.160.118:27017')
