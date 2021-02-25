import requests
from datetime import datetime
import pandas as pd

def get_trades_for_symbol(symbol):
    try:
        url = f"https://arkfunds.io/api/v1/etf/trades?symbol={symbol}&period=1d"
        response = requests.get(url)
        return response.json()
    except:
        return None

def is_valid_trade_data(fund,date):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    if fund is None: return False
    try:
        return (fund['date_from'] == fund['date_to'] and fund['date_from']==date)
    except Exception as exc:
        print(exc)
        return False

def get_ark_trades(date=None,latest=False):
    combined_data = []
    for fund in ["ARKF","ARKG","ARKK","ARKW","ARKQ"]:

        data = get_trades_for_symbol(symbol=fund)
        data_date = data['date_from']
        if not latest:
            if not is_valid_trade_data(data,date):
                continue
        for trade in data['trades']:
            combined_data.append({
                'Fund':data['symbol'],
                'B/S':trade['direction'],
                'Ticker':trade['ticker'],
                'Shares':trade['shares'],
                'ETF %':trade['etf_percent']
            })
    if combined_data == []: return None,None
    return pd.DataFrame().from_records(combined_data),data_date