import discord
import os
from dotenv import load_dotenv

class Client(discord.Client):
    async def on_ready(self):
        print('Logged on {0}'.format(self.user))


    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))


load_dotenv()
client = Client()
client.run(os.getenv("TOKEN"))