import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import json
import argparse
import copy

from src.Mean_Reversion_Test import *
from src.Mean_Reversion_Train import *
from src.Trading_Strategies import *
from src.util import *


def main():
    TRAIN_DATE = pd.Timestamp('2022-01-01')
    MAX_HOLDING = 100
    MAX_TRANSACTION = 10000

    parser = argparse.ArgumentParser(description='Train and test mean reversion trading strategy on S&P 500 companies.')
    parser.add_argument('--train_date', type=str, help='Date to train the model up to. Format: YYYY-MM-DD')
    set_of_stocks = parser.add_mutually_exclusive_group()
    set_of_stocks.add_argument('--snp_500', action='store_true', help='Use S&P 500 companies as the set of stocks.')
    set_of_stocks.add_argument('--small_snp_500', action='store_true', help='Use a small subset of S&P 500 companies as the set of stocks.')
    set_of_stocks.add_argument('--single_company', type=str, help='Use a custom set of stocks.')
    parser.add_argument('--train', action='store_true', help='Retrain the models.')
    parser.add_argument('--parse_snp_tickers', action='store_true', help='Parse the S&P 500 companies.')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output.')
    parser.add_argument('--get_market_cap', action='store_true', help='Get ticker market cap (run daily).')
    args = parser.parse_args()


    if args.parse_snp_tickers:
        parse_snp_tickers()
    if args.train_date:
        TRAIN_DATE = pd.Timestamp(args.train_date)
        
    # small_snp_500_tickers = ["AAPL", "MSFT", "JNJ", "GOOG", "PG"]
    # small_snp_500_tickers = ["AVGO", "ALTM", "CCL", "JNUG", "META", "PLUG", "TSCO"]
    small_snp_500_tickers = ["MMM", "NCLH", "UAL", "AAPL"]
    if args.snp_500:
        with open('data/snp.json', 'r') as f:
            tickers = json.load(f)
    elif args.small_snp_500:
        tickers = small_snp_500_tickers
    elif args.single_company:
        tickers = [args.single_company]
    else:
        tickers = small_snp_500_tickers

    historic_price = {}
    for ticker in tickers:
        download = yf.download(ticker)
        historic_price[ticker] = download['Adj Close']


    if args.train:
        failed_tickers = []
        for TICKER in historic_price.keys():
            try:
                # if TICKER + "_" + TRAIN_DATE.strftime('%Y-%m-%d') + ".keras" not in os.listdir('Models/'):
                print("Training model for ", TICKER, ". Started.")
                training_prices = historic_price[TICKER][:TRAIN_DATE]
                testing_prices = historic_price[TICKER][TRAIN_DATE:]
                train("Models/" + TICKER + "_" + TRAIN_DATE.strftime('%Y-%m-%d') + ".keras", training_prices)
                print("Trained model for ", TICKER, ". Finished " + str(list(historic_price.keys()).index(TICKER) + 1) + " out of " + str(len(historic_price.keys())) + " models.")
            except:
                print("Failed to train model for ", TICKER)
                failed_tickers.append(TICKER)
                pass


    predictions = {}
    testing_prices = {}
    failed_tickers = []
    for TICKER in tickers:
        try:
            testing_prices[TICKER] = historic_price[TICKER][TRAIN_DATE:]
            predictions[TICKER] = test("Models/" + TICKER + "_" + TRAIN_DATE.strftime('%Y-%m-%d') + ".keras", testing_prices[TICKER])
            testing_prices[TICKER] = testing_prices[TICKER][MAX_HOLDING:]
        except:
            failed_tickers.append(TICKER)
            print("No model exists for ", TICKER)
            pass

    for ticker in failed_tickers:
        historic_price.pop(ticker)
        tickers.remove(ticker)
        testing_prices.pop(ticker)
    with open('data/failed_tickers.json', 'w') as f:
        json.dump(failed_tickers, f)

    if args.get_market_cap:
        get_market_cap(TRAIN_DATE + pd.Timedelta(days=MAX_HOLDING), tickers)
    market_cap = json.load(open('data/market_cap.json', 'r'))

    account = Account()
    stocks = {}
    for TICKER in tickers:
        stocks[TICKER] = Stock(TICKER, testing_prices[TICKER].iloc[0])


    net_worth = trade_index_with_confidence_as_duration(MAX_HOLDING, MAX_TRANSACTION, account, copy.deepcopy(stocks), testing_prices, predictions, args.verbose)

    final = net_worth[-1] + abs(account.min_balance)
    initial = abs(account.min_balance)

    if args.verbose and args.single_company:
        plt.plot(testing_prices[list(testing_prices.keys())[0]].keys(), predictions[list(testing_prices.keys())[0]])
        plt.show()

    print("Total return: ", ((final - initial) / initial) * 100, "%")

    print("Index return: ", base_index_return(stocks, market_cap, testing_prices), "%")

    print("Base reutrn: ", base_return(testing_prices), "%")

    plt.plot(testing_prices[list(testing_prices.keys())[0]].keys(), net_worth)
    plt.show()


if __name__ == "__main__":
    main()