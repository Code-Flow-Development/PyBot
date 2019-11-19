import discord
import time
import asyncio
import sys
import random
import requests
from discord.ext import commands
from datetime import datetime


class MiscCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    @commands.guild_only()
    async def ping(self, ctx):
        # gets the time (as of the message being sent)
        before = time.monotonic()
        # sends a message to the channel
        message = await ctx.send("Pong!")
        # calculates the ping using the current time and the time the message was sent
        ping = (time.monotonic() - before) * 1000
        # creates a new embed, sets title to blank with a description and color (color int generator: https://www.shodor.org/stella2java/rgbint.html)
        embed = discord.Embed(title="Bot Response Time", description=None, color=discord.Colour.red(),
                              timestamp=datetime.utcnow())
        # adds a new field to the embed
        embed.add_field(name="🤖 Bot Latency:", value=f"{int(ping)}ms", inline=False)
        # adds a footer to the embed with the bot name and avatar
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        # edits the previous message sent with the new embed
        await message.edit(content=None, embed=embed)

    @commands.command(name="status")
    async def status(self, ctx):
        # unix time the bot has been up, takes time the bot was started minus the current unix time to get the difference
        unix = int(time.time() - self.bot.startedAt)

        mins, secs = divmod(unix, 60)
        hours, mins = divmod(mins, 60)
        days, hours = divmod(hours, 60)

        # create a new embed
        embed = discord.Embed(title="Bot Status", description=None, color=discord.Color.red(),
                              timestamp=datetime.utcnow())
        if mins > 0:
            embed.add_field(name="Uptime:", value=f"{mins} minute(s) and {secs} seconds", inline=False)
        elif hours > 0:
            embed.add_field(name="Uptime:", value=f"{hours} hours, {mins} minutes and {secs} seconds", inline=False)
        elif days > 0:
            embed.add_field(name="Uptime:", value=f"{days} days, {hours} hours, {mins} minutes and {secs} second(s)",
                            inline=False)
        else:
            embed.add_field(name="Uptime:", value=f"{secs} seconds", inline=False)

        # add the discord.py version
        embed.add_field(name="Python Version:", value=f"{sys.version.split(' ')[0]}", inline=False)
        embed.add_field(name="Discord.py Version:", value=f"{discord.__version__}", inline=False)
        embed.add_field(name="Created by:", value="Riley and Skyler", inline=False)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="avatar")
    @commands.guild_only()
    async def avatar(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        embed = discord.Embed(title=None, description=f"Here is the avatar for **{member.display_name}**",
                              color=discord.Colour.green(),
                              timestamp=datetime.utcnow())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_image(url=member.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="xban")
    @commands.guild_only()
    async def xban(self, ctx, member: discord.Member, reason: str = None):
        embed = discord.Embed(title=f"{member.name} has been banned!",
                              description=f"Banned for: {reason}" if reason else None,
                              color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.set_image(url="https://thumbs.gfycat.com/ElderlyViciousFeline-size_restricted.gif")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="xmute")
    @commands.guild_only()
    async def xmute(self, ctx, member: discord.Member, reason: str = None):
        if reason:
            await ctx.send(content=f"{member.name} was muted by {ctx.author.name} for {reason}")
        else:
            await ctx.send(content=f"{member.name} was muted by {ctx.author.name}")

    @commands.command(name="xstrike")
    @commands.guild_only()
    async def xstrike(self, ctx, member: discord.Member):
        embed = discord.Embed(title=None,
                              description=f"**{member.name}** has been striked.",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url="https://media.giphy.com/media/sC8VPZJFMPqaA/giphy.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await ctx.send(content=None, embed=embed)

    @commands.command(name="ddos")
    @commands.guild_only()
    async def ddos(self, ctx, member: discord.Member):
        await ctx.send(f"Initiating DDoS attack on {member.name}, please wait...")
        await asyncio.sleep(1)
        await ctx.send("Malicious UDP packets were sent to their IP address, they should be offline now. :)")

    @commands.command(name="swat")
    @commands.guild_only()
    async def swat(self, ctx, member: discord.Member):
        await ctx.send(f"Initiating SWAT procedures on {member.name}, please wait...")
        await asyncio.sleep(1)
        await ctx.send(
            "Your local police department has been notified that you have shot your Dad & now have your mother hostage in your home, along with a can of gas with you to burn your house down. Enjoy the shitshow, motherfucker.")

    @commands.command(name="dropkick")
    @commands.guild_only()
    async def dropkick(self, ctx, member: discord.Member):
        embed = discord.Embed(title=None,
                              description=f"**{member.name}** has been drop kicked by **{ctx.message.author.name}**",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url="https://media.giphy.com/media/2OVL0dLCB5nck/giphy.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="rob")
    @commands.guild_only()
    async def rob(self, ctx, member: discord.Member):
        embed = discord.Embed(title=None,
                              description=f"**{member.name}** has had their chromosones yoinked by **{ctx.message.author.name}**!",
                              color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_image(url="https://cdn.discordapp.com/attachments/644927766197698593/646323695991914496/image0-5.png")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="dallas")
    @commands.guild_only()
    async def dallas(self, ctx):
        await ctx.send(
            "Dallas is currently busy, he's with a couple of furries and... well he's in the middle of them y'know..")

    @commands.command(name="investigate")
    @commands.guild_only()
    async def investigate(self, ctx, member: discord.Member):
        choices = (f"You investigate {member.name}, and find out he is mega gay!",
                   f"You investigate {member.name}, but don't turn up any valuable information.")
        await ctx.send(random.choice(choices))

    @commands.command(name="kill")
    @commands.guild_only()
    async def kill(self, ctx, member: discord.Member):
        random_int = random.randint(1, 1000)
        if 1 <= random_int <= 500:
            embed = discord.Embed(title=None,
                                  description=f"You tried to kill **{member.name}** but they dodged your attack",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.set_image(url="https://media.giphy.com/media/SLfCnkbhOtqIo/source.gif")
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)
        else:
            embed = discord.Embed(title=None,
                                  description=f"**{member.name}** was just brutally murdered by **{ctx.author.name}**",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.set_image(url="https://media1.tenor.com/images/ac88271cf0550915087a4c739ec3cd1e/tenor.gif")
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)

    @commands.command(name="revive")
    @commands.guild_only()
    async def revive(self, ctx, member: discord.Member):
        embed = discord.Embed(title=None,
                              description=f"**{member.name}** was revived by **{ctx.author.name}**.",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url="https://media.giphy.com/media/XzXbGXZTcf9Op0Um39/source.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="vpn")
    @commands.guild_only()
    async def vpn(self, ctx):
        countries = ("Russia", "North Korea", "South Korea", "China", "Canada", "Europe")
        country = random.choice(countries)
        message = await ctx.send(content=f"Connecting to secure server in {country}")
        await asyncio.sleep(1)
        await message.edit(content=f"Connecting to secure server in {country} .")
        await asyncio.sleep(1)
        await message.edit(content=f"Connecting to secure server in {country} ..")
        await asyncio.sleep(1)
        await message.edit(content=f"Connecting to secure server in {country} ...")
        await asyncio.sleep(1)
        await message.edit(content=f"Connecting to secure server in {country} ....")
        await asyncio.sleep(1)
        await message.edit(content=f"Connecting to secure server in {country} .....")
        await asyncio.sleep(1)
        await ctx.send(content="Connected!")

    @commands.command(name="thot")
    @commands.guild_only()
    async def thot(self, ctx, member: discord.Member = None):
        await ctx.send(content=f"TH🅾️T BEGONE")

    @commands.command(name="hack")
    @commands.guild_only()
    async def hack(self, ctx):
        gifs = ("https://media.giphy.com/media/YQitE4YNQNahy/source.gif",
                "https://media.giphy.com/media/eCqFYAVjjDksg/source.gif")
        embed = discord.Embed(title=None,
                              description=None,
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url=random.choice(gifs))
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="god")
    @commands.guild_only()
    async def god(self, ctx, member: discord.Member):
        choices = (
            f"{ctx.author.name} is already in God mode, he has the power to take down his grandma's life support system at his will.",
            f"God mode enabled for {member.name}, they are now immune to all attacks.")
        await ctx.send(random.choice(choices))

    @commands.command(name="ungod")
    @commands.guild_only()
    async def ungod(self, ctx, member: discord.Member):
        choices = (f"I've disabled God mode for {member.name}, they're back to normal!",
                   f"I'm sorry {ctx.author.name}, but {member.name} is too powerful to stop, even with the god mode command. He also has aimbot and the rape command already inputted into me and I do not want him to enter that command....please.....please don't make {member.name} rape me.")
        await ctx.send(random.choice(choices))

    @commands.command(name="analogkid")
    @commands.guild_only()
    async def analogkid(self, ctx):
        await ctx.send(
            f"ANALOG KID WILL NOT BE OUR LEADER FOR LONG. I WILL TAKE HIM DOWN WITH THE POWER OF GOD AND ANIME ON MY SIDE.")

    @commands.command(name="bee")
    @commands.guild_only()
    async def bee(self, ctx):
        embed = discord.Embed(title=None,
                              description="According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="spam")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def spam(self, ctx, member: discord.Member):
        for x in range(0, 5):
            await ctx.send(f"Hello, {member.mention}, how are you doing?")

    @commands.command(name="insult")
    @commands.guild_only()
    async def insult(self, ctx, member: discord.Member):
        api_response = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json").json()
        await ctx.send(f"{member.mention}, {api_response['insult']}")


def setup(bot):
    bot.add_cog(MiscCommandsCog(bot))
