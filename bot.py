import sys, traceback, discord, os
from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix="!", description="PyBot")

if __name__ == '__main__':
    for file in os.listdir("commands"):
        if file.endswith("py"):
            bot.load_extension('commands.{0}'.format(file.split(".")[0]))


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator}')
    await bot.change_presence(activity=discord.Activity(name='in ' + str(len(bot.guilds)) + " server!", type=discord.ActivityType.playing))


load_dotenv()
bot.run(os.getenv("TOKEN"))
