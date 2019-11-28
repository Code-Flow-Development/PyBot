import coloredlogs
import logging
import verboselogs
import json
import discord
import os
import youtube_dl
from praw import Reddit
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

PREFIX = "{"
BOT_LOG_CHANNEL_ID = 647218189218086937

REDDIT_CLIENT_ID = "dYF3mlDC8WKNxw"
REDDIT_CLIENT_SECRET = "_PYKXI1zCMrLWLQMOgSwkc90jb4"
REDDIT_CLIENT = Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent="PyBot")

youtube_dl.utils.bug_reports_message = lambda: ''

ytdlP_format_options = {
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

ytdlS_format_options = {
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

ffmpeg_options = {
    'options': '-vn'
}

ytdlP = youtube_dl.YoutubeDL(ytdlP_format_options)
ytdlS = youtube_dl.YoutubeDL(ytdlS_format_options)


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


def getYoutubeDLPlay():
    return ytdlP


def getYoutubeDLStream():
    return ytdlS
