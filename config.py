import coloredlogs
import logging
import verboselogs
import json
import discord
import os
from praw import Reddit
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

PREFIX = "{"
BOT_LOG_CHANNEL_ID = 647218189218086937

REDDIT_CLIENT_ID = "dYF3mlDC8WKNxw"
REDDIT_CLIENT_SECRET = "_PYKXI1zCMrLWLQMOgSwkc90jb4"
REDDIT_CLIENT = Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent="PyBot")


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
    username = os.getenv('MONGODB_USERNAME')
    password = os.getenv('MONGODB_PASSWORD')
    return MongoClient(f"mongodb://{username}:{password}@185.230.160.118:27017")


def getRedditClient():
    return REDDIT_CLIENT
