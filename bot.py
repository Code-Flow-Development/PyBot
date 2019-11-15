import discord
import os

class Client(discord.Client):
    async def on_ready(self):
        print('Logged on {0}'.format(self.user))


    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

client = Client()
client.run('NjQ0OTI3MjQxODU1MzAzNjkx.Xc7JVw.7XODjfC1EJ__G8Ux7vXOQ1QD6Y4')