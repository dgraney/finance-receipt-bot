import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import pandas as pd
from stocks import get_current_price, get_one_day_change
import traceback
import argparse

watching_type = discord.ActivityType.watching

load_dotenv()
class SatelliteBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.ticker = None
        
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        self.update.start()

    @tasks.loop(minutes=1.0)
    async def update(self):
        try:
            price = get_current_price(self.ticker)
            change = get_one_day_change(self.ticker)
            print(f"Updating {self.ticker} price to: {price}")
            price = '{0:.4f}'.format(price)
            for guild in self.guilds:
                await guild.me.edit(nick=f"${price} USD")

            activity = discord.Activity(type=watching_type,name=f"{change}|{self.ticker}")
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

client = SatelliteBot()
client.ticker = ticker
client.run(TOKEN)