import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import json
import copy
import argparse

from src.Mean_Reversion_Test import *
from src.Mean_Reversion_Train import *
from src.Trading_Strategies import *
from src.util import *


TRAIN_DATE = pd.Timestamp('2022-01-01')
MAX_HOLDING = 100
MAX_TRANSACTION = 10000


def main():
    parser = argparse.ArgumentParser(description='Train and test mean reversion trading strategy on S&P 500 companies.')
    parser.add_argument('--train_date', type=str, help='Date to train the model up to. Format: YYYY-MM-DD')
    set_of_stocks = parser.add_mutually_exclusive_group()
    set_of_stocks.add_argument('--snp_500', action='store_true', help='Use S&P 500 companies as the set of stocks.')
    set_of_stocks.add_argument('--small_snp_500', action='store_true', help='Use a small subset of S&P 500 companies as the set of stocks.')
    set_of_stocks.add_argument('--single_company', type=str, help='Use a custom set of stocks.')
    parser.add_argument('--train', action='store_true', help='Retrain the models.')
    parser.add_argument('--parse', action='store_true', help='Parse the S&P 500 companies.')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output.')
    args = parser.parse_args()


    if args.parse:
        parse()
    if args.train_date:
        TRAIN_DATE = pd.Timestamp(args.train_date)
        
    with open('snp.json', 'r') as f:
        snp_500_tickers = json.load(f)
    small_snp_500_tickers = ["AAPL", "MSFT", "JNJ", "GOOG", "PG"]
    if args.snp_500:
        tickers = snp_500_tickers
    elif args.small_snp_500:
        tickers = small_snp_500_tickers
    elif args.single_company:
        tickers = [args.single_company]
    else:
        tickers = small_snp_500_tickers

    historic_price = {}
    starting_market_cap = {}
    for ticker in tickers:
        download = yf.download(ticker)
        starting_market_cap[ticker] = yf.Ticker(ticker).info['marketCap']
        historic_price[ticker] = download['Adj Close']


    if args.train:
        failed_tickers = []
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
                failed_tickers.append(TICKER)
                pass

        with open('failed_tickers.json', 'w') as f:
            json.dump(failed_tickers, f)


    predictions = {}
    testing_prices = {}
    for TICKER in historic_price.keys():
        testing_prices[TICKER] = historic_price[TICKER][TRAIN_DATE:]
        predictions[TICKER] = test("Models/" + TICKER + "_" + TRAIN_DATE.strftime('%Y-%m-%d') + ".keras", testing_prices[TICKER])
        testing_prices[TICKER] = testing_prices[TICKER][MAX_HOLDING:]
    testing_prices_for_base = copy.deepcopy(testing_prices)


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


if __name__ == "__main__":
    main()