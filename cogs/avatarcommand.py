import discord
from discord.ext import commands
from datetime import datetime


class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar")
    @commands.guild_only()
    async def avatar(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        embed = discord.Embed(title=f"Avatar for {member.display_name}", description=None, color=discord.Colour.red(),
                              timestamp=datetime.utcnow())
        embed.set_image(url=member.avatar_url)
        await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(AvatarCog(bot))
