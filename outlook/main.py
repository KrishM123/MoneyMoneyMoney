import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.abspath('../'))

from utils.ml_util import *
from utils.trading_util import *
from outlook.src.train import train
from outlook.src.infer import infer
from outlook.src.trading import simple_trade

FEATURE_KERNEL_SIZES = [5, 10, 20, 50, 70, 100]
MAX_HOLDING = 100
tickers = ['JPM', 'BAC', 'WFC']
test_train_split = pd.Timestamp('2020-01-01')

stocks = {}
p_outlook = {}
test_prices = {}
historic_prices = {}

for tkr in tickers:
    historic_prices[tkr] = yf.download(tkr)['Adj Close']
    train_price, test_prices[tkr] = historic_prices[tkr][tkr][:test_train_split].to_list(), historic_prices[tkr][tkr][test_train_split:].to_list()

    train("models/" + tkr + "_" + test_train_split.strftime('%Y-%m-%d') + ".keras", train_price, FEATURE_KERNEL_SIZES, MAX_HOLDING)
    
    p_outlook[tkr] = infer("models/" + tkr + "_" + test_train_split.strftime('%Y-%m-%d') + ".keras", test_prices[tkr], FEATURE_KERNEL_SIZES)

    test_prices[tkr] = test_prices[tkr][max(FEATURE_KERNEL_SIZES) - 1:]

    stocks[tkr] = Stock(tkr, test_prices[tkr][0])


account = Account()

net_worth = simple_trade(account, stocks, test_prices, p_outlook)

market_cap = get_market_cap('eval_data/market_cap.json', test_train_split + pd.Timedelta(days=max(FEATURE_KERNEL_SIZES)), tickers)
index_returns = base_index_return(market_cap, abs(account.min_balance))


# Set up the figure and subplots
plt.figure(figsize=(15, 8))

# Plot net worth and index returns
plt.subplot(1, 2, 1)
plt.plot(index_returns, label="Index Returns", linewidth=2, color='blue')
plt.plot(net_worth, label="Net Worth", linewidth=2, color='green')
plt.title("Net Worth vs. Index Returns")
plt.xlabel("Time Steps")
plt.ylabel("Value")
plt.legend()
plt.grid(True)

# Plot p_outlook for each ticker
plt.subplot(1, 2, 2)
for tkr, outlook in p_outlook.items():
    plt.plot(outlook, label=f"{tkr} P_Outlook", linewidth=1.5)
plt.title("P_Outlook Over Time")
plt.xlabel("Time Steps")
plt.ylabel("P_Outlook")
plt.legend()
plt.grid(True)

# Display the charts
plt.tight_layout()
plt.show()