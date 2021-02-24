import requests
from datetime import datetime
import pandas as pd

def get_trades_for_symbol(symbol):
    try:
        url = f"https://arkfunds.io/api/v1/etf/trades?symbol={symbol}&period=1d"
        response = requests.get(url)
        print(response)
        return response.json()
    except:
        return None

def is_valid_trade_data(fund,date):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    print(date)
    if fund is None: return False
    try:
        return (fund['date_from'] == fund['date_to'] and fund['date_from']==date)
    except Exception as exc:
        print(exc)
        return False

def get_ark_trades(date=None):
    combined_data = []
    for fund in ["ARKF","ARKG","ARKK","ARKW","ARKQ"]:

        data = get_trades_for_symbol(symbol=fund)

        if not is_valid_trade_data(data,date):
            print ("INVALID")
            print(data)
            continue
        for trade in data['trades']:
            combined_data.append({
                'Fund':data['symbol'],
                'B/S':trade['direction'],
                'Ticker':trade['ticker'],
                'Shares':trade['shares'],
                'ETF %':trade['etf_percent']
            })
    if combined_data == []: return None
    return pd.DataFrame().from_records(combined_data)