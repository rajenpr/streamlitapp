import streamlit as st
import pymongo
import yfinance as yf
import pandas as pd

# MongoDB Connection String (Replace with your actual credentials)
mongo_conn_str = "mongodb+srv://prajendr:Mazda123@cluster0.5hmuadl.mongodb.net/stocksuggappdb?retryWrites=true&w=majority"

# Initialize connection to MongoDB
client = pymongo.MongoClient(mongo_conn_str)
db = client["stocksuggappdb"]
collection = db.stocksuggappcol

def insert_trade(data):
    collection.insert_one(data)

def get_trades_by_status(status):
    return list(collection.find({"status": status}))

def update_trade_status(trade_id, new_status, last_known_price=None):
    if last_known_price:
        collection.update_one({"_id": trade_id}, {"$set": {"status": new_status, "last_known_price": last_known_price}})
    else:
        collection.update_one({"_id": trade_id}, {"$set": {"status": new_status}})

def get_current_price(ticker):
    ticker_final = ticker + '.NS'
    stock = yf.Ticker(ticker_final)
    history = stock.history().tail(1)
    if not history.empty:
        return history['Close'].iloc[0]
    else:
        return None

def display_trades(trades, title):
    table_data = []

    for trade in trades:
        if trade['status'] == 'open':
            current_price = get_current_price(trade['ticker_symbol'])
            if current_price is not None and current_price >= trade['target_price']:
                update_trade_status(trade['_id'], "closed", last_known_price=current_price)
                trade['status'] = "closed"
                potential_gain_formatted = "Target Achieved"
            else:
                potential_gain = ((trade['target_price'] - current_price) / current_price) * 100
                potential_gain_formatted = "{:.2f}".format(potential_gain)
        else:
            current_price = trade.get('last_known_price', "N/A")
            potential_gain_formatted = "Trade Closed"

        table_data.append({
            "Stock": f"{trade['stock_name']} ({trade['ticker_symbol']})",
            "Entry Price": "{:.2f}".format(trade['entry_price']),
            "Target Price": "{:.2f}".format(trade['target_price']),
            "Current Price": "{:.2f}".format(current_price) if current_price != "N/A" else current_price,
            "Duration": trade['duration'],
            "Potential Gain (%)": potential_gain_formatted,
            "Status": trade['status']
        })

    trades_df = pd.DataFrame(table_data)
    st.subheader(title)
    st.table(trades_df)

# Streamlit Interface
st.title("Stock Trading App")

# Input form
with st.form("stock_input"):
    st.subheader("Enter New Trade Details")
    stock_name = st.text_input("Stock Name")
    ticker_symbol = st.text_input("Ticker Symbol")
    entry_price = st.number_input("Entry Price", min_value=0.0, format="%.2f")
    target_price = st.number_input("Target Price", min_value=0.0, format="%.2f")
    duration = st.selectbox("Duration of Trade", ["Short Term", "Medium Term", "Long Term"])
    submitted = st.form_submit_button("Submit")
    if submitted:
        trade_data = {
            "stock_name": stock_name,
            "ticker_symbol": ticker_symbol,
            "entry_price": entry_price,
            "target_price": target_price,
            "duration": duration,
            "status": "open"
        }
        insert_trade(trade_data)
        st.success("Trade data submitted!")

# Display sections for Open and Closed trades
if st.button("Refresh Trades"):
    open_trades = get_trades_by_status("open")
    closed_trades = get_trades_by_status("closed")

    display_trades(open_trades, "Open Trades")
    display_trades(closed_trades, "Closed Trades")
