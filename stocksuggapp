import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Streamlit interface for MongoDB connection testing
st.title('MongoDB Connection Test')

uri = st.text_input("Enter your MongoDB URI", value="mongodb+srv://<username>:<password>@<your-cluster-url>")

if st.button('Test Connection'):
    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        st.success("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        st.error(f"Error: {e}")

