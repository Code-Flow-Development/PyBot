import discord
from discord.ext import commands


class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states = {}

    @commands.has_permissions(manage_channels=True)
    @commands.command(pass_context=True, name="lockdown")
    async def lockdown(self, ctx):
        """Lock message sending in the channel."""
        try:
            server = ctx.message.guild
            overwrites_everyone = ctx.message.channel.overwrites_for(server.default_role)
            for channel in server.channels:
                if channel.id in self.states:
                    return
                states = []
                for a in ctx.message.guild.roles:
                    states.append([a, channel.overwrites_for(a).send_messages])
                self.states[channel.id] = states
                overwrites_everyone.send_messages = False
                await channel.set_permissions(server.default_role, overwrite=overwrites_everyone)
                # for modrole in mod_roles:
                #     await ctx.message.channel.set_permissions(modrole, overwrite=overwrites_owner)
            await ctx.send(
                "🔒 All Channels locked!")
        except discord.errors.Forbidden:
            await ctx.send(self.bot.bot_prefix + "Missing permissions.")

    @commands.has_permissions(manage_channels=True)
    @commands.command(pass_context=True, name="unlock")
    async def unlock(self, ctx):
        """Unlock message sending in the channel."""
        print(self.states)
        try:
            for channel in ctx.message.guild.channels:
                if channel.id not in self.states:
                    return
                for a in self.states[channel.id]:
                    overwrites_a = channel.overwrites_for(a[0])
                    overwrites_a.send_messages = a[1]
                    await channel.set_permissions(a[0], overwrite=overwrites_a)
                self.states.pop(channel.id)
            await ctx.send("🔓 All Channels unlocked!")
        except discord.errors.Forbidden:
            await ctx.send(self.bot.bot_prefix + "Missing permissions.")


def setup(bot):
    bot.add_cog(Lockdown(bot))
