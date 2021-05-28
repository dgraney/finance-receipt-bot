from inspect import trace
import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone,UTC
import re
from receipt_parser import parse_receipt_messages,get_hot_tickers
from ark_api import get_ark_trades
import traceback

reported_dates=[]
ark_reported_dates=[]


tz = timezone('EST')
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RECEIPTS_CHANNEL_ID = int(os.getenv('RECEIPTS_CHANNEL')) # 804054712491180034 for EBITDADDIES
ETF_CHANNEL_ID = int(os.getenv('ETF_CHANNEL')) 
RECEIPTS_ROLE_ID = int(os.getenv('RECEIPTS_ROLE'))
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE'))
MOD_ROLE_ID = int(os.getenv('MOD_ROLE'))

CONSECUTIVE_LOL_COUNTER = {}

CONSECUTIVE_MSG_COUNTER = {} 
CURRENT_CONSECUTIVE_MSG = ""

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # await client.wait_until_ready()
    check_receipts.start()
    check_ark_trades.start()

@client.event
async def on_message(ctx):
    global CURRENT_CONSECUTIVE_MSG
    if ctx.author == client.user:
        return
    # ADMIN / MOD COMMANDS
    if is_mod_or_admin(ctx):
        if ctx.content == "!postreceipts":
            await check_receipts(force=True)

    if ctx.content == "!hottrades":
        await check_receipts(force=True,channel_id=ctx.channel.id)
    if ctx.content == "!arktrades":
        await check_ark_trades(force=True,channel_id=ctx.channel.id)

    if not ctx.channel.id in CONSECUTIVE_MSG_COUNTER.keys():
        CONSECUTIVE_MSG_COUNTER[ctx.channel.id] = 0
    
    if ctx.content == CURRENT_CONSECUTIVE_MSG:
        CONSECUTIVE_MSG_COUNTER[ctx.channel.id] = CONSECUTIVE_MSG_COUNTER[ctx.channel.id] + 1
    else:
        CONSECUTIVE_MSG_COUNTER[ctx.channel.id] = 0

    CURRENT_CONSECUTIVE_MSG = ctx.content

    if CONSECUTIVE_MSG_COUNTER[ctx.channel.id] > 2:
        CONSECUTIVE_MSG_COUNTER[ctx.channel.id] = 0
        channel = client.get_channel(ctx.channel.id)
        await channel.send(CURRENT_CONSECUTIVE_MSG)


@tasks.loop(minutes=5.0)
async def check_receipts(force=False,channel_id=RECEIPTS_CHANNEL_ID):
    try:
        today_str = datetime.now(tz).strftime("%Y%m%d")

        # Only trigger at 4 pm
        if not force:
            if datetime.now(tz).hour != 16:
                print("Not triggering receipt check... Waiting on market close! Current time: ",datetime.now(tz))
                return
            if today_str in reported_dates:
                return # We already reported today.
        receipts_channel = client.get_channel(RECEIPTS_CHANNEL_ID)
        channel = client.get_channel(channel_id)
        start_of_market = datetime.now(tz).replace(hour=1,minute=0)
        
        # Get last 200 messages in that channel
        messages = await receipts_channel.history(limit=200).filter(
            lambda m:
                m.created_at.replace(tzinfo=UTC).astimezone(tz) > start_of_market and
                m.author != client.user
        ).flatten()
        
        df = parse_receipt_messages(messages)

        # Analyze Data
        hot_tickers = get_hot_tickers(df)
        hot_ticker_str = f"```{hot_tickers.to_string(index=False)}```"

        if not force:
            await channel.send(f"<@&{RECEIPTS_ROLE_ID}>")
        await channel.send(":fire:**TODAY'S HOT TICKERS**:fire:")
        await channel.send(hot_ticker_str)

        if not force:
            reported_dates.append(today_str)
    except Exception as exc:
        traceback.print_exc()

@tasks.loop(minutes=5.0)
async def check_ark_trades(force=False,channel_id=ETF_CHANNEL_ID):
    print("checking ark trades...")
    try:
        today_str = datetime.now(tz).strftime("%Y-%m-%d")
        yesterday_str = datetime.now(tz).strftime("%Y-%m-%d")
        
        if not force:
            if today_str in ark_reported_dates: return

        channel = client.get_channel(channel_id) # Needs to be the right channel...

        if force:
            df,trade_date = get_ark_trades(latest=True) # Just get the latest dataset
        else:
            df,trade_date = get_ark_trades() # Only get the data if it's for today
            if df is None: 
                return

        ark_trades_str = f"```{df.to_string(index=False,justify='center')}\nSource: arkfunds.io```"

        # Get cathie emoji
        emoji = discord.utils.get(client.emojis, name='cathie')

        if force:
            await channel.send(f"{str(emoji)}**ARK TRADES ({trade_date})**{str(emoji)}")
        else:
            await channel.send(f"{str(emoji)}**TODAY'S ARK TRADES ({trade_date})**{str(emoji)}")
        await channel.send(ark_trades_str)

        if not force:
            ark_reported_dates.append(today_str)
    except:
        traceback.print_exc()

@tasks.loop(minutes=5.0)
async def good_morning(channel_id=787712409111494686):
    try:
        today_str = datetime.now(tz).strftime("%Y%m%d")

        if datetime.now(tz).hour != 8:
            print("Not triggering receipt check... Waiting on market close! Current time: ",datetime.now(tz))
            return
        if today_str in reported_dates:
            return # We already reported today.
        
        mm_channel = client.get_channel(channel_id)
        await mm_channel.send("gm")
        
    except Exception as exc:
        traceback.print_exc()

def is_mod_or_admin(ctx):
    try:
        mod = discord.utils.get(ctx.guild.roles, id=MOD_ROLE_ID)
        admin = discord.utils.get(ctx.guild.roles, id=ADMIN_ROLE_ID)

        author_roles = ctx.author.roles
        return (mod in author_roles or admin in author_roles)
    except: 
        return False

client.run(TOKEN)

# parse_single_message('Buy 40 SNPR @ 40.00')