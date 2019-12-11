import discord
import random
import re
import requests
from datetime import datetime
from discord.ext import commands
from utils import getLogger, ServerSettings, RedditClient
from .utils.checks import isNSFWEnabled

gfycat_regex = re.compile(r'(https://gfycat.com/(.*))(\?.*)?')
imgur_regex = re.compile(r'(https://i.imgur.com/(.*))(\?.*)?')
reddit_regex = re.compile(r'(https://i.redd.it/(.*))(\?.*)?')

ENABLED = True


class NSFWCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="boobs", hidden=True, enabled=ENABLED)
    @commands.has_role("NSFW Tester")
    @commands.is_nsfw()
    @commands.guild_only()
    @isNSFWEnabled()
    async def boobs(self, ctx):
        server_document = ServerSettings(ctx.guild).getServerSettings()
        if server_document["modules"]["nsfw_commands"]:
            boob_subreddits = ["boobs", "Boobies", "Bigtitssmalltits", "naturaltitties", "BustyPetite"]
            subreddit = random.choice(boob_subreddits)
            posts = Reddit().RedditClient().getRedditClient().subreddit(subreddit).new(limit=100)
            post = random.choice([x for x in posts])
            print(post.url)

            if gfycat_regex.match(post.url):
                direct_link = await getGfycatDirect(post.url)
                if direct_link:
                    embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                          timestamp=datetime.utcnow())
                    embed.set_image(url=direct_link)
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    return await ctx.send(content=None, embed=embed)
            elif imgur_regex.match(post.url) or reddit_regex.match(post.url):
                embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
                embed.set_image(url=post.url)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                getLogger().debug(post.url)
                return await ctx.send(content=None, embed=embed)
            else:
                await ctx.send(f"Nothing found :(")
                return self.boobs(ctx)

    @commands.command(name="boobdrop", hidden=True, enabled=ENABLED)
    @commands.has_role("NSFW Tester")
    @commands.is_nsfw()
    @commands.guild_only()
    @isNSFWEnabled()
    async def boobdrop(self, ctx):
        server_document = ServerSettings(ctx.guild).getServerSettings()
        if server_document["modules"]["nsfw_commands"]:
            async with ctx.typing():
                posts = RedditClient().getRedditClient().subreddit("TittyDrop").new(limit=1000)
                post = random.choice([x for x in posts])
                getLogger().debug(f"Post URL: {post.url}")

                if gfycat_regex.match(post.url):
                    direct_link = await getGfycatDirect(post.url)
                elif imgur_regex.match(post.url) or reddit_regex.match(post.url):
                    direct_link = post.url
                else:
                    await ctx.send(f"Nothing found :(")
                    await self.boobdrop(ctx)

                getLogger().debug(f"Direct Link: {direct_link}")

                embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
                embed.set_image(url=direct_link)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            return await ctx.send(content=None, embed=embed)

    @commands.command(name="pussy", hidden=True, enabled=ENABLED)
    @commands.has_role("NSFW Tester")
    @commands.is_nsfw()
    @commands.guild_only()
    @isNSFWEnabled()
    async def pussy(self, ctx):
        server_document = ServerSettings(ctx.guild).getServerSettings()
        if server_document["modules"]["nsfw_commands"]:
            pussy_subreddits = ["pussy", "LipsThatGrip"]
            posts = RedditClient().getRedditClient().subreddit(random.choice(pussy_subreddits)).new(limit=100)
            post = random.choice([x for x in posts])
            print(post.url)

            if gfycat_regex.match(post.url):
                direct_link = await getGfycatDirect(post.url)
                if direct_link:
                    embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                          timestamp=datetime.utcnow())
                    embed.set_image(url=direct_link)
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    return await ctx.send(content=None, embed=embed)
            elif imgur_regex.match(post.url) or reddit_regex.match(post.url):
                embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
                embed.set_image(url=post.url)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                getLogger().debug(post.url)
                return await ctx.send(content=None, embed=embed)
            else:
                return await ctx.send(f"Nothing found :(")

    @commands.command(name="ass", hidden=True, enabled=ENABLED)
    @commands.has_role("NSFW Tester")
    @commands.is_nsfw()
    @commands.guild_only()
    @isNSFWEnabled()
    async def ass(self, ctx):
        server_document = ServerSettings(ctx.guild).getServerSettings()
        if server_document["modules"]["nsfw_commands"]:
            ass_subreddits = ["asshole", "AssOnTheGlass", "SpreadEm", "booty_gifs"]
            posts = RedditClient().getRedditClient().subreddit(random.choice(ass_subreddits)).new(limit=100)
            post = random.choice([x for x in posts])
            print(post.url)

            if gfycat_regex.match(post.url):
                direct_link = await getGfycatDirect(post.url)
                if direct_link:
                    embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                          timestamp=datetime.utcnow())
                    embed.set_image(url=direct_link)
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    return await ctx.send(content=None, embed=embed)
            elif imgur_regex.match(post.url) or reddit_regex.match(post.url):
                embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
                embed.set_image(url=post.url)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                getLogger().debug(post.url)
                return await ctx.send(content=None, embed=embed)
            else:
                return await ctx.send(f"Nothing found :(")

    @commands.command(name="nsfw", hidden=True, enabled=ENABLED)
    @commands.has_role("NSFW Tester")
    @commands.is_nsfw()
    @commands.guild_only()
    @isNSFWEnabled()
    async def nsfw(self, ctx):
        server_document = ServerSettings(ctx.guild).getServerSettings()
        if server_document["modules"]["nsfw_commands"]:
            nsfw_subreddits = ["nsfw", "NSFW_GIFS", "squirting", "pussy", "whenitgoesin", "scissoring", "boobs", "gonewild",
                               "RealGirls", "OnOff", "bdsm", "Bondage", "pawg", "PetiteGoneWild", "GirlsWithToys",
                               "NSFW_4K", "NsfwAss", "60fpsporn", "NSFW_HTML5", "iWantToFuckHer", "HighResNSFW",
                               "nsfwhardcore", "celebnsfw", "Amateur", "Nsfw_Amateurs", "ass", "bigasses", "anal",
                               "asshole", "AssOnTheGlass", "SpreadEm", "booty_gifs", "SheLikesItRough", "facesitting",
                               "curvy", "petite", "xsmallgirls", "collegesluts", "CollegeAmateurs", "collegensfw",
                               "Gonewild18", "gonewildcouples", "gwcumsluts", "workgonewild", "LegalTeens", "Just18",
                               "barelylegalteens", "Barelylegal", "LipsThatGrip", "rearpussy", "Boobies", "TittyDrop",
                               "Bigtitssmalltits", "BustyPetite", "naturaltitties"]
            posts = RedditClient().getRedditClient().subreddit(random.choice(nsfw_subreddits)).new(limit=100)
            post = random.choice([x for x in posts])
            print(post.url)

            if gfycat_regex.match(post.url):
                direct_link = await getGfycatDirect(post.url)
                if direct_link:
                    embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                          timestamp=datetime.utcnow())
                    embed.set_image(url=direct_link)
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    return await ctx.send(content=None, embed=embed)
            elif imgur_regex.match(post.url) or reddit_regex.match(post.url):
                embed = discord.Embed(title=f"{post.title}", description=None, color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
                embed.set_image(url=post.url)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                getLogger().debug(post.url)
                return await ctx.send(content=None, embed=embed)
            else:
                return await ctx.send(f"Nothing found :(")


async def getGfycatDirect(link):
    try:
        gfycat_id = link.split("/")[-1].split("-")[0].split("?")[0]
        response = requests.get(f"https://api.gfycat.com/v1/gfycats/{gfycat_id}").json()
        return response["gfyItem"]["gifUrl"]
    except Exception as e:
        getLogger().error(f"[NSFWCommands] boobdrop; Error: {e}")
        return None


def setup(bot):
    bot.add_cog(NSFWCommands(bot))
