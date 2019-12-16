import asyncio
import os
import platform
import sys
import time
from datetime import datetime

import discord
import requests
from discord.ext import commands

from utils import ServerSettings


class UtilityCommandsCog(commands.Cog):
    """Utility and Commands with no specific category"""

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
        embed.add_field(name="\> Bot",
                        value=f"**Servers:** {len(self.bot.guilds)}\n**Users:**: {member_count}\n**Uptime:** {uptime_format}")
        embed.add_field(name="\> System",
                        value=f"**Library:** Discord.py {discord.__version__}\n**Python Version:** {sys.version.split(' ')[0]}\n**OS:** {platform.system()} {platform.release()} ({os.name})")
        embed.add_field(name="\> Created by", value="- Puyodead1\n- Loco\n- Unity", inline=False)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="help")
    async def help(self, ctx, category: str = None):
        ignored = ("Events", "GuildEvents", "Example")
        cogs = [y for y in [{'name': name.split("Cog")[0], 'description': cog.description, 'cog': cog} for name, cog in
                            self.bot.cogs.items()] if not y["name"] in ignored]

        if category is None:
            # show the main help menu

            embed = discord.Embed(title=f"**Command Categories**",
                                  description="To view help for a category, use ``help <category name> (ex ``help funcommands``) \n - - -",
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            for cog in cogs:
                embed.add_field(name=cog['name'], value=cog['description'], inline=False)

            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

            await ctx.send(content=None, embed=embed)
        else:
            category = category.lower()
            categories = [x["name"].lower() for x in cogs]
            if category in categories:
                # valid category
                try:
                    cog = [x["cog"] for x in cogs if x["name"].lower() == category][0]
                    command_list = cog.get_commands()
                    pagination = [command_list[i:i + 5] for i in range(0, len(command_list), 5)]
                    page = 0
                    embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - **{category}**",
                                          description=f"{cog.description} \n - - -",
                                          color=discord.Color.green(),
                                          timestamp=datetime.utcnow())

                    for command in pagination[page]:
                        embed.add_field(name=command.name, value=command.help, inline=False)

                    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

                    command_list_message = await ctx.send(content=None, embed=embed)
                    if page + 2 <= 1 or page + 2 < len(pagination):
                        await command_list_message.add_reaction("➡")
                    await command_list_message.add_reaction("❌")

                    await self.process_reactions(ctx, command_list_message, page, pagination, cog, category)
                except IndexError:
                    return await ctx.send(f"Invalid category")

    @commands.command(name="userinfo", help="Shows detailed information on a user", usage="[@user or user id]")
    async def user_info(self, ctx, member: discord.Member = None):
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

    @commands.command(name="addmessageresponse", help="Add a custom message response", usage="<trigger> <response>",
                      aliases=["amr"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def add_message_response(self, ctx, trigger: str, response: str):
        server_settings = ServerSettings(ctx.guild)
        server_document = server_settings.getServerSettings()
        custom_message_responses = server_document["custom_message_responses"]
        current_triggers = [x["trigger"] for x in custom_message_responses]
        if trigger not in current_triggers:
            new_trigger = {
                "trigger": trigger,
                "response": response
            }
            server_document["custom_message_responses"].append(new_trigger)
            server_settings.update("settings", server_document)
            embed = discord.Embed(title=f"Message Response has been added!", description=None,
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        else:
            await ctx.send(f"{trigger} is already added!")

    @commands.command(name="listmessageresponses", help="List custom message responses for the server", aliases=["lmr"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def list_responses(self, ctx):
        server_document = ServerSettings(ctx.guild)
        server_settings = server_document.getServerSettings()
        responses_list = server_settings["custom_message_responses"]
        new_list = []
        for response in responses_list:
            response_dict = dict(response)
            new_list.append(
                f"{len(new_list) + 1}. Trigger: {response_dict['trigger']}; Response: {response_dict['response']}")
        embed = discord.Embed(title=f"Active Message Responses", description='\n'.join(new_list),
                              color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="deletemessageresponse", help="Delete a custom message response from the server",
                      aliases=["dmr", "rmr", "removemessageresponse"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def delete_response(self, ctx, index):
        server_document = ServerSettings(ctx.guild)
        server_settings = server_document.getServerSettings()
        responses_list: list = server_settings["custom_message_responses"]
        try:
            responses_list.remove(responses_list[int(index) - 1])
            server_document.update("settings", server_settings)
            embed = discord.Embed(title=f"Message Response has been deleted!", description=None,
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            return await ctx.send(content=None, embed=embed)
        except IndexError:
            await ctx.send(f"[Message Responses] Invalid Index", delete_after=10)
        except ValueError:
            await ctx.send(f"[Message Responses] Invalid Index", delete_after=10)

    async def process_reactions(self, ctx, message, page, pagination, cog, category):
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=90.0,
                                                     check=lambda r, u: u == ctx.message.author)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            return await ctx.send(f"Timed out", delete_after=10)
        else:
            if reaction.emoji == "➡":
                page += 1
                new_embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - **{category}**",
                                          description=f"{cog.description}\n - - -",
                                          color=discord.Color.green(),
                                          timestamp=datetime.utcnow())

                for command in pagination[page]:
                    new_embed.add_field(name=command.name, value=command.help, inline=False)

                new_embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                new_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await message.clear_reactions()

                if page + 1 >= 1 or page + 1 == len(pagination):
                    await message.add_reaction("⬅")
                if page + 1 <= 1 or page + 1 < len(pagination):
                    await message.add_reaction("➡")
                await message.add_reaction("❌")

                await message.edit(content=None, embed=new_embed)
                await self.process_reactions(ctx, message, page, pagination, cog, category)
            elif reaction.emoji == "⬅":
                page -= 1
                new_embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - **{category}**",
                                          description=f"{cog.description}\n - - -",
                                          color=discord.Color.green(),
                                          timestamp=datetime.utcnow())

                for command in pagination[page]:
                    new_embed.add_field(name=command.name, value=command.help, inline=False)

                new_embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                new_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await message.clear_reactions()
                if page - 1 >= 1 or page - 1 == len(pagination):
                    await message.add_reaction("⬅")
                if page - 1 <= 1 or page + 1 < len(pagination):
                    await message.add_reaction("➡")
                await message.add_reaction("❌")

                await message.edit(content=None, embed=new_embed)
                await self.process_reactions(ctx, message, page, pagination, cog, category)
            elif reaction.emoji == "❌":
                await message.delete()


def setup(bot):
    bot.add_cog(UtilityCommandsCog(bot))
