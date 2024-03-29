import streamlit as st
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import numpy as np
import datetime as dt
import pytz


APCA_API_KEY_ID = st.secrets["APCA_API_KEY_ID"]
APCA_API_SECRET_KEY = st.secrets["APCA_API_SECRET_KEY"]
APCA_API_BASE_URL = st.secrets.get("APCA_API_BASE_URL", 'https://paper-api.alpaca.markets')

api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, base_url=APCA_API_BASE_URL)

# Define your backtesting parameters here
rs_bars = 15
smoothing_constant = 3
rs_ma_bars = 20 
vfi_period = 130
vfi_smooth = 2
vfi_crit = 0 
maxlossperc = 7 
vfi_coef = 0.2
vfi_vol_coef = 2.5
lookback_window = 130
# Define your signal processing functions here (calculate_rsmk, calculate_vfi, determine_signal)

def get_historical_bars(api, ticker, lookback_days):
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    past_date = timeNow - dt.timedelta(days=lookback_days)

    bars = api.get_bars(ticker, tradeapi.TimeFrame.Day,
                        start=past_date.isoformat(),
                        end=None,
                        limit=lookback_days)
    return bars

# ... (Insert the functions calculate_rsmk, calculate_vfi, and determine_signal here)
def calculate_rsmk(etf_bars, index_bars, rs_bars, smoothing_constant, rs_ma_bars):
    # Ensure enough data is available
    if len(etf_bars) < rs_bars or len(index_bars) < rs_bars:
        return None, None

    # Convert bars to numpy arrays for calculations
    etf_close = np.array([bar.c for bar in etf_bars])
    index_close = np.array([bar.c for bar in index_bars])

    # Calculate RSMK
    r12 = etf_close[-rs_bars:] / index_close[-rs_bars:]
    rs1 = np.log(r12[-1]) - np.log(r12[0])
    rs = rs1 * 100
    rs_smoothed = np.mean(rs)  # Example of smoothing, can be adjusted

    # Calculate Moving Average of RSMK
    if len(etf_bars) < rs_ma_bars:
        mars = rs_smoothed  # If not enough data for moving average
    else:
        mars = np.mean([np.log(etf_close[i] / etf_close[i - rs_ma_bars]) * 100 for i in range(-rs_ma_bars, 0)])

    return rs_smoothed, mars

def calculate_vfi(bars, period, smooth, coef, vol_coef):
    if len(bars) < max(30, period):
        return None  # Not enough data

    # Extract required data from bars
    closes = np.array([bar.c for bar in bars])
    highs = np.array([bar.h for bar in bars])
    lows = np.array([bar.l for bar in bars])
    volumes = np.array([bar.v for bar in bars])

    # Typical Price and Price Change
    typical_prices = (highs + lows + closes) / 3
    price_changes = typical_prices[1:] - typical_prices[:-1]

    # Standard Deviation of Price Changes
    vinter = np.std(price_changes[-30:])

    # Cut-off Calculation
    cutoff = coef * vinter * closes

    # Volume Average and Maximum Volume
    vave = np.mean(volumes[-period:])
    vmax = vave * vol_coef

    # Volume Cut-off Point
    vc = np.minimum(volumes[-period:], vmax)

    # Volume Force
    mf = typical_prices - np.roll(typical_prices, 1)
    vcp = np.where(mf > cutoff[-period:], vc, np.where(mf < -cutoff[-period:], -vc, 0))

    # VFI Calculation
    vfi = np.sum(vcp) / vave

    return vfi

def determine_signal(api, symbol, index_symbol, rs_bars, smoothing_constant, rs_ma_bars, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef, vfi_crit):
    # Fetch historical data for ETF and Index
    etf_bars = get_historical_bars(api, symbol, rs_ma_bars + rs_bars)
    index_bars = get_historical_bars(api, index_symbol, rs_ma_bars + rs_bars)

    if not etf_bars or not index_bars:
        return 'hold'  # Not enough data

    # Calculate RSMK and VFI
    rsmk, mars = calculate_rsmk(etf_bars, index_bars, rs_bars, smoothing_constant, rs_ma_bars)
    vfi = calculate_vfi(etf_bars, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef)

    # Decision Logic
    if rsmk > mars and vfi > vfi_crit:
        return 'buy'
    elif rsmk < mars or vfi < vfi_crit:
        return 'sell'
    else:
        return 'hold'
def is_bear_market(index_bars, lookback_period=30, threshold=0.90):
    if len(index_bars) < lookback_period:
        return False  # Not enough data

    moving_average = np.mean([bar.c for bar in index_bars[-lookback_period:]])
    current_price = index_bars[-1].c

    return current_price < moving_average * threshold
# Define your trading logic here
# Define your trading logic
def trade_logic(api):
    
    # Fetch current account information
    account = api.get_account()
    cash_available = float(account.cash)
    #print(f"Current cash available: ${cash_available:.2f}")
    returnString = f"[Current cash available: ${cash_available:.2f}]" 
    # Define the symbols
    symbols = ['VUG', 'VTV']
    index_symbol = 'SPY'

    # Fetch historical data using get_bars
    
    vug_bars = get_historical_bars(api, 'VUG', lookback_days=lookback_window)
    vtv_bars = get_historical_bars(api, 'VTV', lookback_days=lookback_window)
    spy_bars = get_historical_bars(api, 'SPY', lookback_days=lookback_window)

    # print(vug_bars)
    # print(vtv_bars)
    # print(spy_bars)    

    # Calculate the RSMK and VFI signals
    signals = {}
    for symbol, etf_bars in zip(symbols, [vug_bars, vtv_bars]):
        # Calculate RSMK and VFI for each ETF
        rsmk, mars = calculate_rsmk(etf_bars, spy_bars, rs_bars, smoothing_constant, rs_ma_bars)
        vfi = calculate_vfi(etf_bars, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef)
        if rsmk > mars and vfi > vfi_crit:
            signal = 'buy' 
        elif rsmk < mars or vfi < vfi_crit:
            signal = 'sell' 
        else:
            signal = 'hold'
        #print(f"Signal for {symbol}: {signal}")
        returnString = returnString + f"\n[Signal for {symbol}: {signal}]"
        signals[symbol] = signal
        

    # Get a list of current positions
    positions = api.list_positions()
    positions_dict = {position.symbol: position for position in positions}

    if is_bear_market(spy_bars):
        #print("Bear market conditions detected, not executing trades.")
        returnString = returnString + "\n[Bear market conditions detected, not executing trades.]"
        return returnString
    for symbol in signals:
            current_price = [bar.c for bar in (vug_bars if symbol == 'VUG' else vtv_bars)][-1]  # Current price is the close of the last bar
            signal = signals[symbol]
            
            

            # Execute trades based on the signal
            if signal == 'buy' and cash_available >= current_price:
                # Buy if the signal is 'buy' and there's enough cash
                api.submit_order(
                    symbol=symbol,
                    qty=1,  # Replace with your desired quantity
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
               # print(f"Submitted order to buy {symbol} at {current_price} as signal is {signal}")
                returnString = returnString + f"\n[Submitted order to buy {symbol} at {current_price} as signal is {signal}]"
            elif signal == 'buy' and cash_available < current_price:
               # print(f"Not enough cash to buy {symbol} at {current_price}")
                returnString = returnString + f"\n[Not enough cash to buy {symbol} at {current_price}]"

            if signal == 'sell' and symbol in positions_dict:
                # Sell if the signal is 'sell' and you own the ETF
                position_qty = int(positions_dict[symbol].qty)
                api.submit_order(
                    symbol=symbol,
                    qty=position_qty,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
              #  print(f"Submitted order to sell {position_qty} of {symbol} at {current_price} as signal is {signal}")
                returnString = returnString + f"\n[Submitted order to sell {position_qty} of {symbol} at {current_price} as signal is {signal}]"
            elif signal == 'sell' and symbol not in positions_dict:
                returnString = returnString + f"\n[No {symbol} position to sell]"
    return returnString            
           
        
        



