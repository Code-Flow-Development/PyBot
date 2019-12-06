import asyncio
import random
from datetime import datetime

import discord
import requests
from discord import Forbidden, HTTPException, InvalidArgument, NotFound
from discord.ext import commands
from prawcore import exceptions

from utils import getRandomFact, RedditClient


class FunCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar", help="View a large version of a users avatar", usage="[@user]",
                      description="Defaults to author if no user is specified")
    @commands.guild_only()
    async def avatar(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        embed = discord.Embed(title=None,
                              color=discord.Colour.green(),
                              timestamp=datetime.utcnow())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_image(url=member.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="xban", usage="<@user>")
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

    @commands.command(name="xmute", usage="<@user>")
    @commands.guild_only()
    async def xmute(self, ctx, member: discord.Member, reason: str = None):
        if reason:
            await ctx.send(content=f"{member.name} was muted by {ctx.author.name} for {reason}")
        else:
            await ctx.send(content=f"{member.name} was muted by {ctx.author.name}")

    @commands.command(name="xstrike", usage="<@user>")
    @commands.guild_only()
    async def xstrike(self, ctx, member: discord.Member):
        embed = discord.Embed(title=None,
                              description=f"**{member.name}** has been striked.",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url="https://media.giphy.com/media/sC8VPZJFMPqaA/giphy.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await ctx.send(content=None, embed=embed)

    @commands.command(name="ddos", help="No internet connection... Check your connection and try again!",
                      usage="<@user>")
    @commands.guild_only()
    async def ddos(self, ctx, member: discord.Member):
        await ctx.send(f"Initiating DDoS attack on {member.name}, please wait...")
        await asyncio.sleep(1)
        await ctx.send("Malicious UDP packets were sent to their IP address, they should be offline now. :)")

    @commands.command(name="swat", help="FBI, OPEN UP!", usage="<@user>")
    @commands.guild_only()
    async def swat(self, ctx, member: discord.Member):
        await ctx.send(f"Initiating SWAT procedures on {member.name}, please wait...")
        await asyncio.sleep(1)
        embed = discord.Embed(title=None,
                              description="Your local police department has been notified that you have shot your Dad & now have your mother hostage in your home, along with a can of gas with you to burn your house down. Enjoy the shitshow, motherfucker.",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url="https://media.tenor.com/images/a1912e38f72c5df9050d931853fafddb/tenor.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="dropkick", help="BA BOOM!", usage="<@user>")
    @commands.guild_only()
    async def dropkick(self, ctx, member: discord.Member):
        embed = discord.Embed(title=None,
                              description=f"**{member.name}** has been drop kicked by **{ctx.message.author.name}**",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        # embed.set_image(url="https://media.giphy.com/media/2OVL0dLCB5nck/giphy.gif")
        embed.set_image(url="https://media.giphy.com/media/YD0sJDzEgueXK/source.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="rob", help="PUT THE CHROMOSOME IN THE BAG!", usage="<@user>")
    @commands.guild_only()
    async def rob(self, ctx, member: discord.Member):
        images = ("https://cdn.discordapp.com/attachments/644927766197698593/646323695991914496/image0-5.png",
                  "https://media1.tenor.com/images/99df9d4636544fe8383c54b36a1ef935/tenor.gif",
                  "https://media1.tenor.com/images/20f243e697a63f526fc9a81600daed50/tenor.gif",
                  "https://media1.tenor.com/images/f3f2ffa2d265f3d64b69d4de1dc2dc17/tenor.gif")
        image = random.choice(images)
        if image == "https://cdn.discordapp.com/attachments/644927766197698593/646323695991914496/image0-5.png":
            embed = discord.Embed(title=None,
                                  description=f"**{member.name}** has had their chromosones yoinked by **{ctx.message.author.name}**!",
                                  color=discord.Color.red(), timestamp=datetime.utcnow())
            embed.set_image(url=image)
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)
        else:
            embed = discord.Embed(title=None,
                                  description=f"**{member.name}** was robbed by **{ctx.message.author.name}**!",
                                  color=discord.Color.red(), timestamp=datetime.utcnow())
            embed.set_image(url=image)
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)

    @commands.command(name="dallas", help="Dallas is a fucking furry")
    @commands.guild_only()
    async def dallas(self, ctx):
        embed = discord.Embed(title=None,
                              description="Dallas is currently busy, he's with a couple of furries and... well he's in the middle of them y'know..",
                              color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_image(url="https://i.imgur.com/wIa2brp.jpg")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="investigate", help="See what you can see!", usage="<@user>")
    @commands.guild_only()
    async def investigate(self, ctx, member: discord.Member):
        choices = (f"You investigate {member.name}, and find out he is mega gay!",
                   f"You investigate {member.name}, but don't turn up any valuable information.")
        await ctx.send(random.choice(choices))

    @commands.command(name="kill", help="U W0T M8!", usage="<@user>")
    @commands.guild_only()
    async def kill(self, ctx, member: discord.Member):
        random_int = random.randint(1, 1000)
        if member == ctx.author:
            if 1 <= random_int <= 500:
                embed = discord.Embed(title=None,
                                      description=f"You just committed suicide!",
                                      color=discord.Color.green(), timestamp=datetime.utcnow())
                embed.set_image(url="https://media1.tenor.com/images/1547113c4d7cbfe1b6d41b4211edf096/tenor.gif")
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                return await ctx.send(content=None, embed=embed)
            else:
                embed = discord.Embed(title=None,
                                      description=f"You tried to kill yourself!",
                                      color=discord.Color.green(), timestamp=datetime.utcnow())
                embed.set_image(url="https://media1.tenor.com/images/e349f19d4c0f48abf4a8cdfceb3bf151/tenor.gif")
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                return await ctx.send(content=None, embed=embed)

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

    @commands.command(name="revive", help="Help a friend in need!", usage="<@user>")
    @commands.guild_only()
    async def revive(self, ctx, member: discord.Member):
        embed = discord.Embed(title=None,
                              description=f"**{member.name}** was revived by **{ctx.author.name}**.",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url="https://media.giphy.com/media/XzXbGXZTcf9Op0Um39/source.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="vpn", help="The most secure vpn!")
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

    @commands.command(name='lenny', help='Lenny faces')
    @commands.guild_only()
    async def lenny(self, ctx):
        faces = (
            "( ͡° ͜ʖ ͡°)", "( ͠° ͟ʖ ͡°)", "( ͡~ ͜ʖ ͡°)", "( ͡ʘ ͜ʖ ͡ʘ)", "( ͡o ͜ʖ ͡o)", "(° ͜ʖ °)", "( ‾ʖ̫‾)",
            "( ಠ ͜ʖಠ)",
            "( ͡° ʖ̯ ͡°)", "( ͡ಥ ͜ʖ ͡ಥ)", "༼  ͡° ͜ʖ ͡° ༽", "(▀̿Ĺ̯▀̿ ̿)", "( ✧≖ ͜ʖ≖)", "(ง ͠° ͟ل͜ ͡°)ง",
            "(͡ ͡° ͜ つ ͡͡°) ",
            "[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]", "(✿❦ ͜ʖ ❦)", "ᕦ( ͡° ͜ʖ ͡°)ᕤ", "( ͡° ͜ʖ ͡°)╭∩╮", "¯\_( ͡° ͜ʖ ͡°)_/¯",
            "(╯ ͠° ͟ʖ ͡°)╯┻━┻", "( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)", "¯\_(ツ)_/¯", "ಠ_ಠ")
        await ctx.send(content=f"{random.choice(faces)}")

    @commands.command(name='fact', help='Random did you know facts')
    @commands.guild_only()
    async def fact(self, ctx):
        fact = getRandomFact()
        await ctx.send(content=f"Did you know? {fact}")

    @commands.command(name="thot", help="THOT BEGONE", usage="[@user]")
    @commands.guild_only()
    async def thot(self, ctx, member: discord.Member = None):
        await ctx.send(content=f"TH🅾️T BEGONE")

    @commands.command(name="hack", help="Become a l33t h4x0r")
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

    @commands.command(name="god", help="Enable god mode", usage="<@user>")
    @commands.guild_only()
    async def god(self, ctx, member: discord.Member):
        choices = (
            f"{ctx.author.name} is already in God mode, he has the power to take down his grandma's life support system at his will.",
            f"God mode enabled for {member.name}, they are now immune to all attacks.")
        await ctx.send(random.choice(choices))

    @commands.command(name="ungod", help="Disable god mode", usage="<@user>")
    @commands.guild_only()
    async def ungod(self, ctx, member: discord.Member):
        choices = (f"I've disabled God mode for {member.name}, they're back to normal!",
                   f"I'm sorry {ctx.author.name}, but {member.name} is too powerful to stop, even with the god mode command. He also has aimbot and the rape command already inputted into me and I do not want him to enter that command....please.....please don't make {member.name} rape me.")
        await ctx.send(random.choice(choices))

    @commands.command(name="analogkid", help="WITH THE POWER OF GOD AND ANIME!")
    @commands.guild_only()
    async def analogkid(self, ctx):
        await ctx.send(
            f"ANALOG KID WILL NOT BE OUR LEADER FOR LONG. I WILL TAKE HIM DOWN WITH THE POWER OF GOD AND ANIME ON MY SIDE.")

    @commands.command(name="bee", help="According to all known laws of aviation")
    @commands.guild_only()
    async def bee(self, ctx):
        embed = discord.Embed(title=None,
                              description="According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="immaheadout", help="Imma head out")
    @commands.guild_only()
    async def immaheadout(self, ctx):
        embed = discord.Embed(title=None,
                              description=None,
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url="https://cdn.discordapp.com/attachments/644927766197698593/646136209940414464/image0.jpg")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="alexjones", help="YOU'RE NOT AN INTELLECTUAL!")
    @commands.guild_only()
    async def alex_jones(self, ctx):
        embed = discord.Embed(title=None,
                              description=None,
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(url="https://media.discordapp.net/attachments/644927766197698593/647167462315393053/ezgif.com-video-to-gif.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="cybertruck", help="That might have been a little *too* hard")
    @commands.guild_only()
    async def cyber_truck(self, ctx):
        embed = discord.Embed(title="oops" if random.randint(0, 100) > 50 else None,
                              description=None,
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/645773103296675880/651548504870617088/tesla-oops.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="whothefuckjustpingedme", aliases=["whotfpingedme", "whotfjustpingedme", "wtfjpm"])
    @commands.guild_only()
    async def who_just_pinged_me(self, ctx):
        embed = discord.Embed(title=None,
                              description=None,
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(
            url="https://media.discordapp.net/attachments/363695761004691456/645734741575729188/ac3.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="gnome")
    @commands.guild_only()
    async def gnomed(self, ctx):
        embed = discord.Embed(title=None,
                              description=None,
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(
            url="https://puyodead1.wtf/u/MEQGPSiVr1.gif")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="confusion")
    @commands.guild_only()
    async def confusion(self, ctx):
        embed = discord.Embed(title=None,
                              description=None,
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_image(
            url="https://i.imgur.com/i7CecBP.jpg")
        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="spam", help="Spams a user with 5 mentions", usage="<@user>", hidden=True, enabled=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def spam(self, ctx, member: discord.Member):
        for x in range(0, 5):
            await ctx.send(f"Hello {member.mention}, how are you doing?")

    @commands.command(name="spamrole", help="Spams a role with 5 mentions", usage="<@role>", hidden=True, enabled=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def spamrole(self, ctx, role: discord.Role):
        for x in range(0, 5):
            await ctx.send(
                f"Hello {role.mention}, how are you doing?" if not "everyone" in role.name else f"Hello {role}, how are you doing?")

    @commands.command(name="insult", help="Insult a user", usage="<@user>")
    @commands.guild_only()
    async def insult(self, ctx, member: discord.Member):
        api_response = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json").json()
        await ctx.send(f"{member.mention}, {api_response['insult']}")

    @commands.command(name="roulette",
                      help="Take a chance of being muted, kicked, banned, or being safe! Too scared? use 'dry' mode to see what WOULD have happened to you!",
                      usage="[dry]")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True, kick_members=True, manage_roles=True)
    async def roulette(self, ctx, mode: str = "default"):
        if mode == "default":
            if ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_roles or ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.kick_members:
                await ctx.send(f"You cannot use this command because you have moderator permissions!")
                return
            # 0=kick, 1=ban, 2=mute, 3=nothing
            choice = random.randint(0, 3)
            if choice == 0:
                embed = discord.Embed(title=None,
                                      description=f"{ctx.message.author.mention}, Congratulations! You are getting kicked!",
                                      color=discord.Color.green(), timestamp=datetime.utcnow())
                embed.set_image(url="https://media1.tenor.com/images/ca1bad80a757fa8b87dacd9c051f2670/tenor.gif")
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await ctx.send(content=None, embed=embed)
                try:
                    await ctx.author.kick()
                except Forbidden as e:
                    await ctx.send(f"[FunCommands] Missing permission! Error: {e.text}")
                except HTTPException as e:
                    await ctx.send(f"[FunCommands] Failed to kick user {ctx.author.name}! Error: {e.text}")
            elif choice == 1:
                embed = discord.Embed(title=None,
                                      description=f"{ctx.message.author.mention}, Congratulations! You are getting banned!",
                                      color=discord.Color.green(), timestamp=datetime.utcnow())
                embed.set_image(url="https://media1.tenor.com/images/d31dd258cb91c52733fd17d62f997d6f/tenor.gif")
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await ctx.send(content=None, embed=embed)
                try:
                    await ctx.author.ban()
                except Forbidden as e:
                    await ctx.send(f"[FunCommands] Missing permission! Error: {e.text}")
                except HTTPException as e:
                    await ctx.send(f"[FunCommands] Failed to ban user {ctx.author.name}! Error: {e.text}")
            elif choice == 2:
                embed = discord.Embed(title=None,
                                      description=f"{ctx.message.author.mention}, Congratulations! You are getting muted!",
                                      color=discord.Color.green(), timestamp=datetime.utcnow())
                embed.set_image(url="https://media1.tenor.com/images/4fc52cf612af7611598efcb6b788d5e0/tenor.gif")
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await ctx.send(content=None, embed=embed)
                try:
                    muted_role = [x for x in ctx.guild.roles if x.name == "Muted"]
                    muted_role = muted_role[0] if len(muted_role) == 1 else None
                    # check length of the list, if 0 no muted role, if > 0 there is one or more
                    if muted_role:
                        try:
                            await ctx.author.add_roles(muted_role, reason="Roulette", atomic=False)
                        except Forbidden as e:
                            await ctx.send(f"[FunCommands] Missing permission! Error: {e.text}")
                        except HTTPException as e:
                            await ctx.send(f"[FunCommands] Failed to add role! Error: {e.text}")
                    else:
                        # create the role
                        try:
                            muted_role = await ctx.guild.create_role(name="Muted", reason="No muted role existed",
                                                                     permissions=discord.Permissions.none())
                            # loop channels and add muted role permissions
                            for channel in [x for x in ctx.guild.channels]:
                                try:
                                    await channel.set_permissions(muted_role, send_messages=False, add_reactions=False,
                                                                  manage_messages=False, embed_links=False,
                                                                  attach_files=False,
                                                                  external_emojis=False)
                                    print(f"Set permissions on channel {channel.name}")
                                except Forbidden as e:
                                    # no permission to edit channel specific permissions
                                    await ctx.send(f"[FunCommands] Missing permission! Error: {e.text}")
                                except NotFound as e:
                                    await ctx.send(
                                        f"[FunCommands] The role or member being edited is not part of the guild! Error: {e.text}")
                                except HTTPException as e:
                                    await ctx.send(
                                        f"[FunCommands] Editing channel specific permissions failed for channel `{channel.name}`! Error: {e.text}")
                                except InvalidArgument as e:
                                    await ctx.send(
                                        f"[FunCommands] The overwrite parameter is invalid or the target type was not role or member! Error: {e}")

                            try:
                                await ctx.author.add_roles(muted_role, reason="Roulette", atomic=False)
                            except Forbidden as e:
                                await ctx.send(f"[FunCommands] Missing permission! Error: {e.text}")
                            except HTTPException as e:
                                await ctx.send(f"[FunCommands] Failed to add role! Error: {e.text}")
                        except Forbidden as e:
                            # no permission to create the role
                            await ctx.send(f"[FunCommands] Cannot create muted role, Missing "
                                           f"permission! Error: {e.text}")
                        except HTTPException as e:
                            # Creating role failed
                            await ctx.send(f"[FunCommands] Failed to create muted role! Error: {e.text}")
                        except InvalidArgument as e:
                            # Invalid keyword was given
                            await ctx.send(f"[FunCommands] Invalid keyword given! Error: {e}")
                except HTTPException as e:
                    # Retrieving roles failed
                    await ctx.send(f"[FunCommands] Retrieving roles failed! Error: {e.text}")
            elif choice == 3:
                embed = discord.Embed(title=None,
                                      description=f"{ctx.message.author.mention}, Congratulations! You are safe!",
                                      color=discord.Color.green(), timestamp=datetime.utcnow())
                embed.set_image(url="https://media1.tenor.com/images/275eb7164f29563897c7d51d74edbf19/tenor.gif")
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await ctx.send(content=None, embed=embed)
        elif mode == "dry":
            choice = random.randint(0, 3)
            if choice == 0:
                await ctx.send(f"You would have been kicked!")
            elif choice == 1:
                await ctx.send(f"You would have been banned!")
            elif choice == 2:
                await ctx.send(f"You would have been muted!")
            elif choice == 3:
                await ctx.send(f"You would have been safe!")

    @commands.command(name="meme", usage="[r/{subreddit name}] [top, rising, new, hot, random]",
                      help="Gets a meme from r/funny or another subreddit",
                      description="Defaults to new if no listing type is specified")
    async def meme(self, ctx, subreddit: str = "funny", listing_type: str = "new"):
        # NOTE: posts that dont contain images will throw an error
        valid_types = ["new", "top", "rising", "hot"]
        if not listing_type.lower() in valid_types:
            return await ctx.send(
                f"{listing_type.lower()} is not a valid type! Valid types are: "
                f"```top\nhot\nnew\nbest\nrandom\nrising\ntop```")

        try:
            # get a post
            post = getPostsByListingType(subreddit, listing_type)

            if post:
                embed = discord.Embed(title=None,
                                      description=post.title,
                                      color=discord.Color.green(), timestamp=datetime.utcnow())
                embed.set_image(url=post.url)
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                return await ctx.send(content=None, embed=embed)
            else:
                return await ctx.send(f"Oops! is that an nsfw subreddit? maybe it was just an nsfw post :/")
        except exceptions.Forbidden:
            return await ctx.send(f"[PRAW] Forbidden!")
        except exceptions.NotFound:
            return await ctx.send(f"[PRAW] Not Found!")
        except Exception as e:
            print(f"[FunCommands] Cought error in meme command! Error: {e}")
            return await ctx.send(f"An error occured!")


def getPostsByListingType(subreddit: str, type: str):
    if type == "top":
        posts = RedditClient().RedditClient().getRedditClient().subreddit(subreddit).top(limit=1)
        post = [x for x in posts][0]
        if post.over_18:
            return
        else:
            return post
    elif type == "rising":
        posts = RedditClient().getRedditClient().subreddit(subreddit).rising(limit=1)
        post = [x for x in posts][0]
        if post.over_18:
            return
        else:
            return post
    elif type == "new":
        posts = RedditClient().getRedditClient().subreddit(subreddit).new(limit=1)
        post = [x for x in posts][0]
        if post.over_18:
            return
        else:
            return post
    elif type == "hot":
        posts = RedditClient().getRedditClient().subreddit(subreddit).hot(limit=1)
        post = [x for x in posts][0]
        if post.over_18:
            getPostsByListingType(subreddit, type)
        else:
            return post
    elif type == "random":
        posts = RedditClient().getRedditClient().subreddit(subreddit).random(limit=1)
        post = [x for x in posts][0]
        if post.over_18:
            return
        else:
            return post


def setup(bot):
    bot.add_cog(FunCommandsCog(bot))
