from Mean_Reversion_Test import *
from Mean_Reversion_Train import *
from Trading_Strategies import *
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import json
import copy

with open('snp.json', 'r') as f:
    snp_500_tickers = json.load(f)

small_snp_500_tickers = ["AAPL", "MSFT", "JNJ", "GOOG", "PG"]

historic_price = {}
starting_market_cap = {}

for ticker in snp_500_tickers:
    download = yf.download(ticker)
    starting_market_cap[ticker] = yf.Ticker(ticker).info['marketCap']
    historic_price[ticker] = download['Adj Close']

TRAIN_DATE = pd.Timestamp('2022-01-01')
MAX_HOLDING = 100

for TICKER in historic_price.keys():
    try:
        if TICKER + "_" + TRAIN_DATE.strftime('%Y-%m-%d') + ".keras" not in os.listdir('Models/'):
            print("Training model for ", TICKER, ". Started.")
            training_prices = historic_price[TICKER][:TRAIN_DATE]
            testing_prices = historic_price[TICKER][TRAIN_DATE:]
            train("Models/" + TICKER + "_" + TRAIN_DATE.strftime('%Y-%m-%d') + ".keras", training_prices)
            print("Trained model for ", TICKER, ". Finished " + str(list(historic_price.keys()).index(TICKER) + 1) + " out of " + str(len(historic_price.keys()) + 1) + " models.")
    except:
        print("Failed to train model for ", TICKER)
        pass

predictions = {}
testing_prices = {}
for TICKER in historic_price.keys():
    testing_prices[TICKER] = historic_price[TICKER][TRAIN_DATE:]
    predictions[TICKER] = test("Models/" + TICKER + "_" + TRAIN_DATE.strftime('%Y-%m-%d') + ".keras", testing_prices[TICKER])
    testing_prices[TICKER] = testing_prices[TICKER][MAX_HOLDING:]
testing_prices_for_base = copy.deepcopy(testing_prices)


MAX_TRANSACTION = 10000
account = Account()
stocks = {}
for TICKER in historic_price.keys():
    stocks[TICKER] = Stock(TICKER, testing_prices[TICKER].iloc[0])
stocks_for_base = copy.deepcopy(stocks)
stocks_for_base2 = copy.deepcopy(stocks)


net_worth = trade_index_with_confidence_as_duration(MAX_HOLDING, MAX_TRANSACTION, account, stocks, testing_prices, predictions)

final = net_worth[-1] + abs(account.min_balance)
initial = abs(account.min_balance)
print("Total return: ", ((final - initial) / initial) * 100, "%")

base_account = Account()
base2_account = Account()
print("Return if you bought shares of the companies according to market cap: ", base_return(base_account, stocks_for_base, testing_prices_for_base, starting_market_cap, MAX_TRANSACTION), "%")
equal_market_cap = {}
for ticker in starting_market_cap.keys():
    equal_market_cap[ticker] = 1
print("Return if you bought equal amout of each company: ", base_return(base2_account, stocks_for_base2, testing_prices_for_base, equal_market_cap, MAX_TRANSACTION), "%")


plt.plot(testing_prices[list(testing_prices.keys())[0]].keys(), net_worth)
plt.show()