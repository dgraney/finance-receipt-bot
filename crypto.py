from requests import Request, Session
import json
import os
from dotenv import load_dotenv


load_dotenv()
CRYPTO_TOKEN = os.getenv(f'CRYPTO_TOKEN')
URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
HEADERS = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': CRYPTO_TOKEN,
}

def get_quote(symbol):
    parameters = {
    'symbol':symbol,
    'convert':'USD'
    }

    session = Session()
    session.headers.update(HEADERS)

    try:
        response = session.get(URL, params=parameters)
        res = json.loads(response.text)
        print(res)
    except Exception as e:
        print(e)
        return "ERR"

    status = res['status']
    data = res['data']
    name = data[symbol]['name']
    quote_USD = round(data[symbol]['quote']['USD']['price'],2)
    quote_USD_1D = round(data[symbol]['quote']['USD']['percent_change_24h'],2)
    return quote_USD,quote_USD_1D
