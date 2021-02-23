import re
import pandas as pd
from stocks import get_one_day_change

buy_order_regex = re.compile(f"(?i)(Buy|Bought|\+|B)")
sell_order_regex = re.compile(f"(?i)(Sell|Sold|\-|S)")

def format_and_split_message(msg):
    for char in "$:@":
        msg = msg.replace(char,'')

    # add spaces where we want to typically
    for char in "+-":
        msg = msg.replace(char,f"{char} ")
    msg = msg.replace(' x ',' ')

    msg_split = msg.split(' ')

    #remove empty strings
    msg_split = list(filter(None, msg_split))
    print(msg_split)
    return msg_split

def parse_single_message(content,author):
    msg_split = format_and_split_message(content)

    if len(msg_split) < 3: return#raise Exception('Message not long enough to parse!')
    order_type = msg_split[0]

    # Check if a buy, sell, or invalid
    buy_order_type_match = buy_order_regex.match(order_type)
    sell_order_type_match = sell_order_regex.match(order_type)

    if not buy_order_type_match and not sell_order_type_match: return None#raise Exception('Message Can't Parse!')

    if buy_order_type_match:    order_type = "Buy"
    else:                       order_type = "Sell"
    
    # Either quantity or price were not set...
    if len(msg_split) == 3:
        try:
            quantity = float(msg_split[1])
            ticker = msg_split[2].upper()
            price = None
        except:
            quantity = None
            ticker = msg_split[1].upper()
            price = float(msg_split[2])
    else:
        quantity = float(msg_split[1])
        ticker = msg_split[2].upper()
        price = float(msg_split[3])

    return {
        "type":order_type,
        "quantity":quantity,
        "ticker":ticker,
        "price":price,
        #"original_msg":content,
        "author":author
    }


def parse_receipt_messages(messages):
    all_data = []
    for m in messages:
        author = m.author
        content = m.content
        for m_ in content.split('\n'):
            print(m_)
            data = parse_single_message(m_,author.name)
            print(data)
            if data is None: continue
            all_data.append(data)
    print(all_data)
    df = pd.DataFrame().from_records(all_data)
    print(df)
    df['total_cost'] = df.apply(lambda row: row['price'] * row['quantity'],axis=1)
    print(df)
    return df

def get_hot_tickers(df):
    # Hot tickers
    order_occurrences = df.groupby(['ticker','author']).size().reset_index().rename(columns={0:'count'})
    hot_tickers = order_occurrences.ticker.value_counts().head(5)
    hot_tickers = pd.DataFrame(hot_tickers).reset_index()

    hot_tickers.columns = ['Ticker','Unique Activity']
    hot_tickers['Server Volume'] = hot_tickers.apply(lambda row: df.loc[df['ticker'] == row['Ticker'],'quantity'].sum(),axis=1)
    hot_tickers['1-Day'] = hot_tickers.apply(lambda row: get_one_day_change(row['Ticker']),axis=1)
    return hot_tickers