import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import pandas as pd
from crypto import get_quote
import traceback
import argparse

watching_type = discord.ActivityType.watching

load_dotenv()
class CryptoBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.ticker = None
        
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        self.update.start()

    @tasks.loop(minutes=3.0)
    async def update(self):
        try:
            price,change = get_quote(self.ticker)
            print(f"Updating {self.ticker} price to: {price}")
            price = '{0:.2f}'.format(price)
            for guild in self.guilds:
                await guild.me.edit(nick=f"{self.ticker}")

            if change <= 0:
                activity = discord.Activity(type=watching_type,name=f"${price}🔴{change}%")
            else:
                activity = discord.Activity(type=watching_type,name=f"${price}🟢{change}%")
            await self.change_presence(activity=activity)
        except:
            traceback.print_exc()
        #await self.dBot.change_presence(activity=discord.Game(next(status)))
    
parser = argparse.ArgumentParser()
parser.add_argument("ticker")
args = parser.parse_args()
ticker = args.ticker

load_dotenv()
TOKEN = os.getenv(f'{ticker}_TOKEN')

client = CryptoBot()
client.ticker = ticker
client.run(TOKEN)