import coloredlogs
import logging
import verboselogs
import json
import discord
import os
import youtube_dl
from threading import Thread
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
    file = open("settings.json", 'r')
    contents = file.read()
    return json.loads(contents)["admins"]


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
    return MongoClient(os.getenv("MONGO_URI"))


def getRedditClient():
    return REDDIT_CLIENT


def getYoutubeDLPlay():
    return ytdlP


def getYoutubeDLStream():
    return ytdlS


class APIServer:
    def __init__(self, partial):
        self.FLASK_THREAD: Thread = Thread(target=partial, daemon=True)

    def getThread(self):
        return self.FLASK_THREAD

    def start(self):
        self.FLASK_THREAD.start()

    def stop(self):
        self.FLASK_THREAD.join()

