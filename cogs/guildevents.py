import discord
from datetime import datetime
from utils import utc_to_epoch
from discord.ext import commands


class GuildEventsHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        log_channel = [x for x in guild.channels if x.name == "logs"]
        if len(log_channel) == 1:
            log_channel = log_channel[0]
            created_at_unix = utc_to_epoch(member.created_at)
            created_date = datetime.fromtimestamp(created_at_unix)
            embed = discord.Embed(title="User joined the server!", description=None, color=discord.Color.green())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="Account created", value=f"{created_date}", inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(content=None, embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        log_channel = [x for x in guild.channels if x.name == "logs"]
        if len(log_channel) == 1:
            log_channel = log_channel[0]
            created_at_unix = utc_to_epoch(member.created_at)
            created_date = datetime.fromtimestamp(created_at_unix)
            joined_at_unix = utc_to_epoch(member.joined_at)
            joined_date = datetime.fromtimestamp(joined_at_unix)
            embed = discord.Embed(title="User left the server!", description=None, color=discord.Color.red())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="Account created", value=f"{created_date}", inline=False)
            embed.add_field(name="Joined", value=f"{joined_date}", inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(GuildEventsHandler(bot))
