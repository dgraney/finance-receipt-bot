import yfinance as yf
import traceback
def get_one_day_change(ticker):
    try:
        ticker_data = yf.Ticker(ticker)
        history = ticker_data.history(period="2d").reset_index()
        today_close = history['Close'][1]
        last_close = history['Close'][0]
        change = 100*(today_close - last_close)/last_close
        change = round(change,2)
        if change < 0:
            change_str = f"({abs(change)}%)"
        else:
            change_str = f"{abs(change)}%"
        return change_str
    except Exception as exc:
        print(exc)
        traceback.print_exc()
        return "N/A"
