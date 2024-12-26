import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import argparse

sys.path.append(os.path.abspath('../'))

from utils.ml_util import *
from utils.trading_util import *
from outlook.src.train import train
from outlook.src.infer import infer
from outlook.src.trading import simple_trade

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Stock analysis and trading simulation.")
parser.add_argument("--no-train", action="store_true", help="Skip training models.")
parser.add_argument("--no-chart", action="store_true", help="Skip plotting charts.")
args = parser.parse_args()

FEATURE_KERNEL_SIZES = [5, 10]
MAX_HOLDING = 100
MAX_HISTORY = 200
tickers = ['JPM', 'BAC', 'WFC']
test_train_split = pd.Timestamp('2017-01-01')

stocks = {}
p_outlook = {}
test_prices = {}
historic_prices = {}

for tkr in tickers:
    historic_prices[tkr] = yf.download(tkr)['Adj Close']
    train_price, test_prices[tkr] = historic_prices[tkr][tkr][:test_train_split].to_list(), historic_prices[tkr][tkr][test_train_split:].to_list()

    if not args.no_train:
        train("models/" + tkr + "_" + test_train_split.strftime('%Y-%m-%d') + ".keras", train_price, FEATURE_KERNEL_SIZES, MAX_HOLDING, MAX_HISTORY)
    
    p_outlook[tkr] = infer("models/" + tkr + "_" + test_train_split.strftime('%Y-%m-%d') + ".keras", test_prices[tkr], FEATURE_KERNEL_SIZES, MAX_HISTORY)
    test_prices[tkr] = test_prices[tkr][MAX_HISTORY + max(FEATURE_KERNEL_SIZES) - 1:]

    stocks[tkr] = Stock(tkr, test_prices[tkr][0])

account = Account()

net_worth = simple_trade(account, stocks, test_prices, p_outlook)

market_cap = get_market_cap('eval_data/market_cap.json', test_train_split + pd.Timedelta(days=max(FEATURE_KERNEL_SIZES)), tickers)
index_returns = base_index_return(market_cap, abs(account.min_balance))

print(account)
print(f"Index Returns: {index_returns[-1] / account.min_balance * 100}%")

if not args.no_chart:
    plt.figure(figsize=(15, 8))

    plt.subplot(1, 2, 1)
    plt.plot(index_returns, label="Index Returns", linewidth=2, color='blue')
    plt.plot(net_worth, label="Net Worth", linewidth=2, color='green')
    plt.title("Net Worth vs. Index Returns")
    plt.xlabel("Time Steps")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    for tkr, outlook in p_outlook.items():
        plt.plot(outlook, label=f"{tkr} P_Outlook", linewidth=1.5)
    plt.title("P_Outlook Over Time")
    plt.xlabel("Time Steps")
    plt.ylabel("P_Outlook")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
