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
historic_prices = {}
p_outlook = {}
test_prices = {}

for tkr in tickers:
    historic_prices[tkr] = yf.download(tkr)['Adj Close']
    train_price, test_prices[tkr] = list(historic_prices[tkr][:test_train_split].values), list(historic_prices[tkr][test_train_split:].values)

    train("models/" + tkr + "_" + test_train_split.strftime('%Y-%m-%d') + ".keras", train_price, FEATURE_KERNEL_SIZES, MAX_HOLDING)
    p_outlook[tkr] = infer("models/" + tkr + "_" + test_train_split.strftime('%Y-%m-%d') + ".keras", test_prices[tkr])

    test_prices[tkr] = test_prices[tkr][max(FEATURE_KERNEL_SIZES) - 1:]

    stocks[tkr] = Stock(tkr, test_prices[tkr][0])

market_cap = get_market_cap('outlook/eval_data/market_cap.json', test_train_split + pd.Timedelta(days=max(FEATURE_KERNEL_SIZES)), tickers)
index_returns = base_index_return(stocks, market_cap, test_prices)

account = Account()

net_worth = simple_trade(account, stocks, test_prices, p_outlook)


normalized_net_worth = [100 * (value / net_worth[0]) for value in net_worth]

plt.figure(figsize=(10, 6))
plt.plot(index_returns, label="Index Returns", linewidth=2)
plt.plot(normalized_net_worth, label="Net Worth", linewidth=2)

plt.title("Net Worth vs. Index Returns")
plt.xlabel("Time Steps")
plt.ylabel("Value (Normalized to 100)")
plt.legend()
plt.grid(True)
plt.show()