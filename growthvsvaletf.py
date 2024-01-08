import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Parameters
start_date = '2023-01-01'
end_date = '2024-01-01'
rs_bars = 15
smoothing_constant = 3
rs_ma_bars = 20
vfi_period = 130
vfi_smooth = 2
vfi_crit = 0
maxlossperc = 7
vfi_coef = 0.2
vfi_vol_coef = 2.5

# Download data from Yahoo Finance
vug_data = yf.download('VUG', start=start_date, end=end_date)
vtv_data = yf.download('VTV', start=start_date, end=end_date)
spy_data = yf.download('SPY', start=start_date, end=end_date)


# Calculate RSMK
def calculate_rsmk(etf_data, index_data, rs_bars, smoothing_constant):
    r12 = etf_data['Close'] / index_data['Close']
    rs1 = np.log(r12) - np.log(r12.shift(rs_bars))
    rs = rs1.ewm(span=smoothing_constant, adjust=False).mean() * 100
    mars = rs.rolling(window=rs_ma_bars).mean()
    return rs, mars

# Calculate VFI
def calculate_vfi(data, period, smooth, coef, vol_coef):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    inter = np.log(typical_price) - np.log(typical_price.shift(1))
    vinter = inter.rolling(window=30).std()
    cutoff = coef * vinter * data['Close']
    vave = data['Volume'].rolling(window=period).mean().shift(1)
    vmax = vave * vol_coef
    vc = np.minimum(data['Volume'], vmax)
    mf = typical_price - typical_price.shift(1)
    vcp = np.where(mf > cutoff, vc, np.where(mf < -cutoff, -vc, 0))
    vfi = pd.Series(np.cumsum(vcp) / vave).ewm(span=smooth, adjust=False).mean()
    return vfi

# Apply calculations
vug_rsmk, vug_mars = calculate_rsmk(vug_data, spy_data, rs_bars, smoothing_constant)
vtv_rsmk, vtv_mars = calculate_rsmk(vtv_data, spy_data, rs_bars, smoothing_constant)
vug_vfi = calculate_vfi(vug_data, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef)
vtv_vfi = calculate_vfi(vtv_data, vfi_period, vfi_smooth, vfi_coef, vfi_vol_coef)

# Backtesting logic
portfolio_value = [10000]  # Starting with initial equity
holding_vug = False  # Initialize holding status for VUG
holding_vtv = False  # Initialize holding status for VTV
cooldown_period = 1  # Days to wait after selling before buying again
last_sell_date = None  # Track the last sell date

for i in range(1, len(vug_data)):
    date = vug_data.index[i]
    can_buy = last_sell_date is None or (date - last_sell_date).days > cooldown_period
    
    # Check if we should buy VUG
    if can_buy and (vug_rsmk[i] > vug_mars[i] or vug_vfi[i] > vfi_crit):
        holding_vug = True
        holding_vtv = False
        purchase_info_vug = (vug_data['Close'][i], date)
        
    # Check if we should buy VTV
    elif can_buy and (vtv_rsmk[i] > vtv_mars[i] or vtv_vfi[i] > vfi_crit):
        holding_vug = False
        holding_vtv = True
        purchase_info_vtv = (vtv_data['Close'][i], date)
    
    # Check if we should sell VUG
    if holding_vug and (vug_data['Close'][i] < purchase_info_vug[0] * (1 - maxlossperc / 100)):
        holding_vug = False
        last_sell_date = date
    
    # Check if we should sell VTV
    if holding_vtv and (vtv_data['Close'][i] < purchase_info_vtv[0] * (1 - maxlossperc / 100)):
        holding_vtv = False
        last_sell_date = date

    # Update portfolio value based on holdings
    if holding_vug:
        portfolio_value.append(portfolio_value[-1] * (vug_data['Close'][i] / vug_data['Close'][i-1]))
    elif holding_vtv:
        portfolio_value.append(portfolio_value[-1] * (vtv_data['Close'][i] / vtv_data['Close'][i-1]))
    else:
        portfolio_value.append(portfolio_value[-1])

    # Debugging outputs
    print(f"Date: {date}, Holding VUG: {holding_vug}, Holding VTV: {holding_vtv}, VUG Close: {vug_data['Close'][i]}, VTV Close: {vtv_data['Close'][i]}")


# Convert portfolio value to a pandas Series
portfolio_value = pd.Series(portfolio_value, index=vug_data.index)

# Plot the results
plt.figure(figsize=(14, 7))
plt.plot(portfolio_value.index, portfolio_value, label='Portfolio Value')
#plt.plot(vug_data.index, vug_data['Close'] / vug_data['Close'][0] * portfolio_value[0], label='VUG Normalized')
#plt.plot(vtv_data.index, vtv_data['Close'] / vtv_data['Close'][0] * portfolio_value[0], label='VTV Normalized')
plt.plot(spy_data.index, spy_data['Close'] / spy_data['Close'][0] * portfolio_value[0], label='S&P 500 Normalized')
plt.title('ETF Rotation Strategy Performance')
plt.xlabel('Date')
plt.ylabel('Normalized Portfolio Value')
plt.legend()
plt.show()