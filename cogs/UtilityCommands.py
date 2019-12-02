import discord
import time
import sys
import platform
import os
import requests
from utils import ServerSettings
from datetime import datetime
from discord.ext import commands


class UtilityCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Bot ping")
    @commands.guild_only()
    async def ping(self, ctx):
        # make a request to discord status page to get latest api ping
        response = requests.get("https://discord.statuspage.io/metrics-display/ztt4777v23lf/day.json").json()
        latest_ping = response["summary"]["last"]
        # gets the time (as of the message being sent)
        before = time.monotonic()
        # sends a message to the channel
        message = await ctx.send("Pong!")
        # calculates the ping using the current time and the time the message was sent
        ping = (time.monotonic() - before) * 1000
        # creates a new embed, sets title to blank with a description and color (color int generator: https://www.shodor.org/stella2java/rgbint.html)
        embed = discord.Embed(title="Bot Response Time", description=None, color=discord.Colour.green(),
                              timestamp=datetime.utcnow())
        # adds a new field to the embed
        embed.add_field(name="🤖 Bot Latency", value=f"{int(ping)}ms", inline=True)
        embed.add_field(name="🌐 API Latency", value=f"{round(self.bot.latency, 2)}ms", inline=True)
        embed.add_field(name="Latest API Ping", value=f"{latest_ping}ms")
        # adds a footer to the embed with the bot name and avatar
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        # edits the previous message sent with the new embed
        await message.edit(content=None, embed=embed)

    @commands.command(name="status", help="Bot status")
    async def status(self, ctx):
        # unix time the bot has been up, takes time the bot was started minus the current unix time to get the difference
        unix = int(time.time() - self.bot.startedAt)

        mins, secs = divmod(unix, 60)
        hours, mins = divmod(mins, 60)
        days, hours = divmod(hours, 60)

        # create a new embed
        embed = discord.Embed(title="Bot Status", description=None, color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        # add the discord.py version
        member_count = len(self.bot.users)
        print(member_count)
        uptime_format = f"{hours} hours, {mins} minutes, and {secs} seconds" if secs > 0 and mins > 0 and hours > 0 else f"{mins} minutes, and {secs} seconds" if secs > 0 and mins > 0 and hours == 0 else f"{secs} seconds" if secs > 0 and mins == 0 and hours == 0 else "Error"
        embed.add_field(name="\> Bot", value=f"**Servers:** {len(self.bot.guilds)}\n**Users:**: {member_count}\n**Uptime:** {uptime_format}")
        embed.add_field(name="\> System", value=f"**Library:** Discord.py {discord.__version__}\n**Python Version:** {sys.version.split(' ')[0]}\n**OS:** {platform.system()} {platform.release()} ({os.name})")
        # embed.add_field(name="Python Version:", value=f"{sys.version.split(' ')[0]}", inline=False)
        # embed.add_field(name="OS:", value=f"{platform.system()} {platform.release()} ({os.name})", inline=False)
        # embed.add_field(name="Discord.py Version:", value=f"{discord.__version__}", inline=False)
        embed.add_field(name="\> Created by", value="- Puyodead1\n- Loco\n- Unity", inline=False)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="help")
    async def help(self, ctx, category: str = None):
        if not category:
            # show the main help menu
            embed = discord.Embed(title=f"**Help Dictionary**",
                                  description="We have a lot of commands, so there is multiple help commands! \n - - -",
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name="Bot Admin Commands", value="{help botadmin", inline=False)
            embed.add_field(name="Fun Commands", value="{help fun", inline=False)
            embed.add_field(name="Game Commands", value="{help game", inline=False)
            embed.add_field(name="Moderation Commands", value="{help moderation", inline=False)
            embed.add_field(name="Utility Commands", value="{help utility", inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        elif category.lower() == "botadmin":
            command_list = [x for x in self.bot.commands if x.cog_name == "BotAdminCommandsCog"]
            embed = discord.Embed(title=f"**Bot Developer Commands**",
                                  description="Commands for the developer of the bot to use. \n - - -",
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())

            for command in command_list:
                embed.add_field(name=command.name, value=command.help, inline=False)

            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        elif category.lower() == "fun":
            command_list = [x for x in self.bot.commands if x.cog_name == "FunCommandsCog"]
            new_list = command_list[0:8]
            embed = discord.Embed(title=f"**Fun Commands**",
                                  description="Just have some fun, you nerd. \n Do 'fun2' for more commands!\n - - - ",
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            for command in new_list:
                embed.add_field(name=command.name, value=command.help, inline=False)

            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        elif category.lower() == "fun2":
            command_list = [x for x in self.bot.commands if x.cog_name == "FunCommandsCog"]
            new_list = command_list[8:16]
            embed = discord.Embed(title=f"**Fun Commands 2**",
                                  description="Just have some fun, you nerd. \n  Do 'fun3' for more commands!\n - - - ",
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())

            for command in new_list:
                embed.add_field(name=command.name, value=command.help, inline=False)

            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        elif category.lower() == "fun3":
            command_list = [x for x in self.bot.commands if x.cog_name == "FunCommandsCog"]
            new_list = command_list[16:32]
            embed = discord.Embed(title=f"**Fun Commands 3**",
                                  description="Just have some fun, you nerd.\n Do 'fun4' for more commands! \n - - - ",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())

            for x in range(16, 32):
                embed.add_field(name=command_list[x].name, value=command_list[x].help, inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        elif category.lower() == "fun4":
            command_list = [x for x in self.bot.commands if x.cog_name == "FunCommandsCog"]
            embed = discord.Embed(title=f"**Fun Commands 4**",
                                  description="Just have some fun, you nerd.\n YOU MADE IT! THE LAST PAGEEEE!\n - - - ",
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name="{meme",
                            value="Reddit memes.",
                            inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        elif category.lower() == "game":
            command_list = [x for x in self.bot.commands if x.cog_name == "GameCommandsCog"]
            embed = discord.Embed(title=f"**Game Commands**",
                                  description="This section of the bot is currently unfinished "
                                              "\nand being worked on! \n - - -",
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            for command in command_list:
                embed.add_field(name=command.name, value=command.help, inline=False)
            # embed.add_field(name="{rpgstart", value="Start your new adventure in our text RPG!", inline=False)
            # embed.add_field(name="{rpgprofile", value="See your profile in the text RPG!", inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        elif category.lower() == "moderation":
            command_list = [x for x in self.bot.commands if x.cog_name == "ModerationCommandsCog"]
            pass

    @commands.command(name="userinfo", help="Shows detailed information on a user", usage="[@user or user id]")
    async def userinfo(self, ctx, member: discord.Member = None):
        status_icons = {"online": 646827558771359755, "idle": 646827558591135794, "dnd": 646826726428639232,
                        "offline": 646827559035600926}
        if not member:
            member = ctx.author

        status = str(member.status)
        role_ids = [x.id for x in member.roles if x.name != "@everyone"]
        roles = []
        for role_id in role_ids:
            roles.append(ctx.guild.get_role(role_id).mention)

        status_icon = self.bot.get_emoji(status_icons[status])
        activity_text = ""
        if member.activity:
            # user has an activity
            if member.activity.type == 4:
                activity_type = "Playing"
            else:
                # playing
                activity_type = str(member.activity.type).split('.')[1].capitalize()
            activity_text = f"**{activity_type}:** {member.activity.name}"
        else:
            activity_type = "Doing"

        embed = discord.Embed(title=f"Information for {member.name}#{member.discriminator}",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.add_field(name="Nickname", value=member.display_name)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Properties", value=f"**Bot:** {member.bot}")
        embed.add_field(name="Presence",
                        value=f"**Status:** {status_icon} {status.capitalize()}\n{activity_text}")
        embed.add_field(name="Created On", value=f"{member.created_at.strftime('%A, %B %d, %Y')}")
        embed.add_field(name="Joined On", value=f"{member.joined_at.strftime('%A, %B %d, %Y')}")
        embed.add_field(name=f"Roles({len(roles)})", value=f"{'|'.join(roles)}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="addmessageresponse", help="Add a custom message response", usage="<trigger> <response>")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def addmessageresponse(self, ctx, trigger: str, response: str):
        server_settings = ServerSettings(ctx.guild)
        server_document = server_settings.getServerDocument()
        custom_message_responses = server_document["custom_message_responses"]
        current_triggers = [x["trigger"] for x in custom_message_responses]
        if trigger not in current_triggers:
            new_trigger = {
                "trigger": trigger,
                "response": response
            }
            server_document["custom_message_responses"].append(new_trigger)
            server_settings.update("settings", server_document)
            await ctx.send(f"Message response added!")
        else:
            await ctx.send(f"{trigger} is already added!")

    @commands.command(name="listmessageresponses", help="List custom message responses for the server", aliases=["lmr"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def listresponses(self, ctx):
        server_document = ServerSettings(ctx.guild)
        server_settings = server_document.getServerDocument()
        responses_list = server_settings["custom_message_responses"]
        new_list = []
        for response in responses_list:
            response_dict = dict(response)
            new_list.append(f"Trigger: {response_dict['trigger']}; Response: {response_dict['response']}")
        embed = discord.Embed(title=f"Active Message Responses", description='\n'.join(new_list), color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(UtilityCommandsCog(bot))
