
# import alpaca_trade_api as tradeapi
# import os
# import yfinance as yf
# import pandas as pd
# import numpy as np

# # Load environment variables
# from dotenv import load_dotenv
# load_dotenv()

# APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
# APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
# APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'

# # Initialize Alpaca API
# api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, base_url=APCA_API_BASE_URL)

# # Define your trading logic - this is where you'd implement the strategy from your backtesting
# def trade_logic():
#     # Fetch real-time data for VUG and VTV
#     vug_data = yf.download('VUG', period='1d', interval='1m')
#     vtv_data = yf.download('VTV', period='1d', interval='1m')
    
#     # Implement your strategy logic to determine buy or sell signals
#     # This is where you would adapt your backtesting signals to work with real-time data
#     # For example:
#     vug_signal = determine_signal(vug_data)
#     vtv_signal = determine_signal(vtv_data)
    
#     # Get the current account information
#     account = api.get_account()
#     cash = float(account.cash)
    
#     # Check if our account is restricted from trading
#     if account.trading_blocked:
#         print("Account is currently restricted from trading.")
#         return
    
#     # Implement buy/sell logic based on signals and account cash
#     if vug_signal == 'buy' and cash >= vug_data['Close'].iloc[-1]:
#         # Buy VUG
#         api.submit_order(
#             symbol='VUG',
#             qty=1,  # You would calculate the correct quantity to buy based on your strategy and cash available
#             side='buy',
#             type='market',
#             time_in_force='gtc'
#         )
#         print("Submitted order to buy VUG")
#     elif vtv_signal == 'buy' and cash >= vtv_data['Close'].iloc[-1]:
#         # Buy VTV
#         api.submit_order(
#             symbol='VTV',
#             qty=1,  # You would calculate the correct quantity to buy based on your strategy and cash available
#             side='buy',
#             type='market',
#             time_in_force='gtc'
#         )
#         print("Submitted order to buy VTV")
    
#     # Implement additional logic for selling or holding based on your strategy
    
# # Run the trading logic
# trade_logic()

# def calculate_rsmk(etf_data, index_data, rs_bars, smoothing_constant, rs_ma_bars):
#     r12 = etf_data['Close'].iloc[-1] / index_data['Close'].iloc[-1]
#     rs1 = np.log(r12) - np.log(etf_data['Close'].iloc[-rs_bars-1] / index_data['Close'].iloc[-rs_bars-1])
#     rs = rs1 * 100
#     mars = etf_data['Close'].rolling(window=rs_ma_bars).apply(lambda x: np.log(x[-1] / x[0]) * 100).iloc[-1]
#     return rs, mars

# def calculate_vfi(data, period, smooth, coef, vol_coef):
#     typical_price = (data['High'].iloc[-1] + data['Low'].iloc[-1] + data['Close'].iloc[-1]) / 3
#     inter = np.log(typical_price) - np.log(data['Close'].iloc[-2])
#     vinter = data['Close'].rolling(window=30).apply(lambda x: np.log(x).diff().std()).iloc[-1]
#     cutoff = coef * vinter * data['Close'].iloc[-1]
#     vave = data['Volume'].rolling(window=period).mean().iloc[-1]
#     vmax = vave * vol_coef
#     vc = min(data['Volume'].iloc[-1], vmax)
#     mf = typical_price - data['Close'].iloc[-2]
#     vcp = vc if mf > cutoff else (-vc if mf < -cutoff else 0)
#     vfi = vcp / vave  # Simplified for the latest value only
#     return vfi

# def determine_signal(etf, index, rs_bars, smoothing_constant, rs_ma_bars, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef, vfi_crit):
#     # Fetch real-time data for ETF and Index
#     etf_data = yf.download(etf, period='1d', interval='1m')
#     index_data = yf.download(index, period='1d', interval='1m')

#     # Calculate RSMK and VFI
#     rs, mars = calculate_rsmk(etf_data, index_data, rs_bars, smoothing_constant, rs_ma_bars)
#     vfi = calculate_vfi(etf_data, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef)

#     # Decide to buy if RSMK and VFI are greater than their respective thresholds
#     if rs > mars and vfi > vfi_crit:
#         return 'buy'
#     else:
#         return 'hold'

# # This function would be called from your trade_logic function
# # Example usage:
# # signal = determine_signal('VUG', 'SPY', 15, 3, 20, 130, 2, 0.2, 2.5, 0)
# # if signal == 'buy':
# #     # Implement your buy logic

# # Call trade_logic periodically, for example, every minute or every day depending on your strategy
# # You may want to use a scheduler like APScheduler for this purpose.


import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import numpy as np
import datetime as dt
import pytz


load_dotenv()  # This loads the .env file at the root of the project

APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL') or 'https://paper-api.alpaca.markets'

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

# Define your trading logic here
# Define your trading logic
def trade_logic(api):
    # Fetch current account information
    account = api.get_account()
    cash_available = float(account.cash)

    # Define the symbols
    symbols = ['VUG', 'VTV']
    index_symbol = 'SPY'

    # Fetch historical data using get_bars
    
    vug_bars = get_historical_bars(api, 'VUG', lookback_days=lookback_window)
    vtv_bars = get_historical_bars(api, 'VTV', lookback_days=lookback_window)
    spy_bars = get_historical_bars(api, 'SPY', lookback_days=lookback_window)

    print(vug_bars)
    print(vtv_bars)
    print(spy_bars)    

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
        print(f"Signal for {symbol}: {signal}")
        signals[symbol] = signal
        

    # Get a list of current positions
    positions = api.list_positions()
    positions_dict = {position.symbol: position for position in positions}

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
            print(f"Submitted order to buy {symbol} at {current_price}")

        elif signal == 'sell' and symbol in positions_dict:
            # Sell if the signal is 'sell' and you own the ETF
            position_qty = int(positions_dict[symbol].qty)
            api.submit_order(
                symbol=symbol,
                qty=position_qty,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            print(f"Submitted order to sell {position_qty} of {symbol} at {current_price}")
        else:
            print(f"Signal is {signal}, nothing to do for {symbol}")

# Run the trading logic
trade_logic(api)


# import alpaca_trade_api as tradeapi
# import os
# from dotenv import load_dotenv
# import numpy as np
# import pandas as pd
# import datetime as dt
# import pytz

# # Load environment variables
# load_dotenv()
# APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
# APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
# APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL') or 'https://paper-api.alpaca.markets'

# # Initialize Alpaca API
# api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, base_url=APCA_API_BASE_URL)

# # Backtesting parameters
# rs_bars = 15
# smoothing_constant = 3
# rs_ma_bars = 20
# vfi_period = 130
# vfi_smooth = 2
# vfi_crit = 0
# max_loss_perc = 7
# vfi_coef = 0.2
# vfi_vol_coef = 2.5
# lookback_window = 130

# # Signal processing functions


# def calculate_rsmk(etf_bars, index_bars, rs_bars, smoothing_constant, rs_ma_bars):
#     # Ensure enough data is available
#     if len(etf_bars) < rs_bars or len(index_bars) < rs_bars:
#         return None, None

#     # Convert bars to numpy arrays for calculations
#     etf_close = np.array([bar.c for bar in etf_bars])
#     index_close = np.array([bar.c for bar in index_bars])

#     # Calculate RSMK
#     r12 = etf_close[-rs_bars:] / index_close[-rs_bars:]
#     rs1 = np.log(r12[-1]) - np.log(r12[0])
#     rs = rs1 * 100
#     rs_smoothed = np.mean(rs)  # Example of smoothing, can be adjusted

#     # Calculate Moving Average of RSMK
#     if len(etf_bars) < rs_ma_bars:
#         mars = rs_smoothed  # If not enough data for moving average
#     else:
#         mars = np.mean([np.log(etf_close[i] / etf_close[i - rs_ma_bars]) * 100 for i in range(-rs_ma_bars, 0)])

#     return rs_smoothed, mars
# def calculate_vfi(bars, period, smooth, coef, vol_coef):
#     if len(bars) < max(30, period):
#         return None  # Not enough data

#     # Extract required data from bars
#     closes = np.array([bar.c for bar in bars])
#     highs = np.array([bar.h for bar in bars])
#     lows = np.array([bar.l for bar in bars])
#     volumes = np.array([bar.v for bar in bars])

#     # Typical Price and Price Change
#     typical_prices = (highs + lows + closes) / 3
#     price_changes = typical_prices[1:] - typical_prices[:-1]

#     # Standard Deviation of Price Changes
#     vinter = np.std(price_changes[-30:])

#     # Cut-off Calculation
#     cutoff = coef * vinter * closes

#     # Volume Average and Maximum Volume
#     vave = np.mean(volumes[-period:])
#     vmax = vave * vol_coef

#     # Volume Cut-off Point
#     vc = np.minimum(volumes[-period:], vmax)

#     # Volume Force
#     mf = typical_prices - np.roll(typical_prices, 1)
#     vcp = np.where(mf > cutoff[-period:], vc, np.where(mf < -cutoff[-period:], -vc, 0))

#     # VFI Calculation
#     vfi = np.sum(vcp) / vave

#     return vfi
# def determine_signal(api, symbol, index_symbol, rs_bars, smoothing_constant, rs_ma_bars, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef, vfi_crit):
#     # Fetch historical data for ETF and Index
#     etf_bars = get_historical_bars(api, symbol, rs_ma_bars + rs_bars)
#     index_bars = get_historical_bars(api, index_symbol, rs_ma_bars + rs_bars)

#     if not etf_bars or not index_bars:
#         return 'hold'  # Not enough data

#     # Calculate RSMK and VFI
#     rsmk, mars = calculate_rsmk(etf_bars, index_bars, rs_bars, smoothing_constant, rs_ma_bars)
#     vfi = calculate_vfi(etf_bars, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef)

#     # Decision Logic
#     if rsmk > mars and vfi > vfi_crit:
#         return 'buy'
#     elif rsmk < mars or vfi < vfi_crit:
#         return 'sell'
#     else:
#         return 'hold'
# def is_bear_market(index_bars, lookback_period=30, threshold=0.90):
#     """
#     Determine if the market is in a bearish trend based on the index's performance.

#     :param index_bars: Historical bars for the index.
#     :param lookback_period: The number of days to consider for the moving average.
#     :param threshold: The percentage of the moving average that the current price must be below to indicate a bear market.
#     :return: True if bear market conditions are met, False otherwise.
#     """
#     if len(index_bars) < lookback_period:
#         return False  # Not enough data

#     moving_average = np.mean([bar.c for bar in index_bars[-lookback_period:]])
#     current_price = index_bars[-1].c

#     return current_price < moving_average * threshold

# # Fetch historical data
# def get_historical_bars(api, ticker, lookback_days):
#     timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
#     past_date = timeNow - dt.timedelta(days=lookback_days)
#     bars = api.get_bars(ticker, tradeapi.TimeFrame.Day, start=past_date.isoformat(), end=None, limit=lookback_days)
#     return bars

# # Trading logic
# def trade_logic(api):
#     account = api.get_account()
#     cash_available = float(account.cash)
#     symbols = ['VUG', 'VTV']
#     index_symbol = 'SPY'
#     vug_bars = get_historical_bars(api, 'VUG', lookback_window)
#     vtv_bars = get_historical_bars(api, 'VTV', lookback_window)
#     spy_bars = get_historical_bars(api, 'SPY', lookback_window)

#     # Calculate signals and trade
#     for symbol, etf_bars in zip(symbols, [vug_bars, vtv_bars]):
#         rsmk, mars = calculate_rsmk(etf_bars, spy_bars, rs_bars, smoothing_constant, rs_ma_bars)
#         vfi = calculate_vfi(etf_bars, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef)
#         signal = determine_signal(rsmk, mars, vfi, vfi_crit)
        
#         # Implement bear market filter, stop loss, and trading logic
#         # ... [Bear market filter and stop loss logic]

#         # Execute trades
#         # ... [Trade execution logic]

# # Schedule to run trade_logic once per day
# # ... [Scheduling logic using APScheduler or similar]

# # Run the trading logic
# trade_logic(api)
