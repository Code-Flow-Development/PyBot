from config import getLogger
from discord.ext import commands


class CommandEventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        getLogger().info(f"[Commands] {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) ran command {ctx.command.name}")


def setup(bot):
    bot.add_cog(CommandEventCog(bot))
