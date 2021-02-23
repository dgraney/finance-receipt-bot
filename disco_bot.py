import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone,UTC
import re
from receipt_parser import parse_receipt_messages,get_hot_tickers
import traceback

reported_dates=[]


tz = timezone('EST')
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
receipts_channel_id = int(os.getenv('RECEIPTS_CHANNEL')) # 804054712491180034 for EBITDADDIES

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # await client.wait_until_ready()
    check_receipts.start()

@client.event
async def on_message(message):
    # if message.content == "!t":
    #     await check_receipts()
    if message.content == "!forcecheck":
        await check_receipts(force=True)

@tasks.loop(minutes=5.0)
async def check_receipts(force=False):
    try:
        today_str = datetime.now(tz).strftime("%Y%m%d")

        # Only trigger at 4 pm
        if not force:
            if datetime.now(tz).hour != 16:
                print("Not triggering receipt check... Waiting on market close! Current time: ",datetime.now(tz))
                return
            if today_str in reported_dates:
                return # We already reported today.

        channel = client.get_channel(receipts_channel_id)
        start_of_market = datetime.now(tz).replace(hour=9,minute=30)
        
        # Get last 200 messages in that channel
        messages = await channel.history(limit=200).filter(
            lambda m:
                m.created_at.replace(tzinfo=UTC).astimezone(tz) > start_of_market and
                m.author != client.user
        ).flatten()
        
        df = parse_receipt_messages(messages)

        # Analyze Data
        hot_tickers = get_hot_tickers(df)
        print(hot_tickers)
        hot_ticker_str = f"```{hot_tickers.to_string(index=False)}```"

        await channel.send(":fire:**TODAY'S HOT TICKERS**:fire:")
        await channel.send(hot_ticker_str)

        reported_dates.append(today_str)
    except Exception as exc:
        traceback.print_exc()


# @check_receipts.before_loop
# async def before_receipts():
#     print('waiting...')
#     await client.wait_until_ready()

client.run(TOKEN)

# parse_single_message('Buy 40 SNPR @ 40.00')