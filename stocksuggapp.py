import streamlit as st
import pymongo
import yfinance as yf

# MongoDB Connection String (Replace with your actual credentials)
mongo_conn_str = "mongodb+srv://prajendr:Mazda123@cluster0.5hmuadl.mongodb.net/stocksuggappdb?retryWrites=true&w=majority"


# Initialize connection to MongoDB
client = pymongo.MongoClient(mongo_conn_str)
db = client["stocksuggappdb"]
collection = db.stocksuggappcol

def insert_trade(data):
    collection.insert_one(data)

def get_open_trades():
    return list(collection.find({"status": "open"}))

def get_current_price(ticker):
    ticker_final=ticker+'.NS'
    stock = yf.Ticker(ticker)
    history = stock.history().tail(1)
    if not history.empty:
        return history['Close'].iloc[0]
    else:
        return None

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

# Display open trades
if st.button("Show Open Trades"):
    open_trades = get_open_trades()
    for trade in open_trades:
        current_price = get_current_price(trade['ticker_symbol'])
        potential_gain = ((trade['target_price'] - current_price) / current_price) * 100
        st.write(f"Stock: {trade['stock_name']} ({trade['ticker_symbol']})")
        st.write(f"Entry Price: {trade['entry_price']}, Target Price: {trade['target_price']}, Current Price: {current_price}")
        st.write(f"Potential Gain: {potential_gain:.2f}%")

