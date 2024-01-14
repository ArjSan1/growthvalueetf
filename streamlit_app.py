import streamlit as st
from alpacatradingstrategy import trade_logic
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os
import re
load_dotenv()  # This loads the .env file at the root of the project

APCA_API_KEY_ID = st.secrets["APCA_API_KEY_ID"]
APCA_API_SECRET_KEY = st.secrets["APCA_API_SECRET_KEY"]
# If APCA_API_BASE_URL is not set in secrets, it will default to 'https://paper-api.alpaca.markets'
APCA_API_BASE_URL = st.secrets.get("APCA_API_BASE_URL", 'https://paper-api.alpaca.markets')

api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, base_url=APCA_API_BASE_URL)

st.title('Growth vs. Value ETF Strategy')

# Button to trigger the trading logic
if st.button('Execute Trade Logic'):
    # Call the trade logic function
    # Display output of the trade logic function
    returnString = trade_logic(api)
    split_strings = re.findall(r'\[.*?\]', returnString)
    #print(split_strings)
    for i in range(len(split_strings)):
        # Remove the first and last character (the brackets) before writing the output
        st.write(split_strings[i][1:-1])
