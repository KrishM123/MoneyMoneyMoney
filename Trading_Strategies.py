from util import *
import pandas as pd

def confidence_as_quantity(MAX_HOLDING, MAX_TRANSACTION, account, stock, testing_prices, predictions):
    net_worth = []

    for pos in range(len(testing_prices)):
        stock.update_price(testing_prices.iloc[pos])

        if float(predictions[pos][0]) > 0:
            account.buy(stock, round(abs((MAX_TRANSACTION / stock.price) * predictions[pos][0]), 3))

        elif float(predictions[pos][0]) < 0:
            account.sell(stock, round(abs((MAX_TRANSACTION / stock.price) * predictions[pos][0] * 2), 3))

        net_worth.append(account.net_worth())
    return net_worth


def confidence_as_duration(MAX_HOLDING, MAX_TRANSACTION, account, stock, testing_prices, predictions):
    net_worth = []
    sell_orders = {}
    min_balance = account.balance

    for pos in range(len(testing_prices)):
        stock.update_price(testing_prices.iloc[pos])

        if float(predictions[pos][0]) > 0:
            account.buy(stock, round(abs((MAX_TRANSACTION / stock.price) * predictions[pos][0]), 3))
            sell_orders[int(inverse_time_effect3(MAX_HOLDING, predictions[pos][0])) + pos] = round(abs((MAX_TRANSACTION / stock.price) * predictions[pos][0]), 3)

        if (pos in sell_orders):
            account.sell(stock, sell_orders[pos])
            sell_orders.pop(pos)
        
        if account.balance < min_balance:
            min_balance = account.balance
        net_worth.append(account.net_worth())
    return net_worth, min_balance

def trade_index_with_confidence_as_duration(MAX_HOLDING, MAX_TRANSACTION, account, stocks, testing_prices, predictions):
    net_worth = []
    sell_orders = {}

    for pos in range(len(testing_prices[list(testing_prices.keys())[0]].keys())):
        for ticker in stocks.keys():

            stocks[ticker].update_price(testing_prices[ticker][pos])

            stock = stocks[ticker]

            if float(predictions[ticker][pos][0]) > 0.8:
                # print('Bought ', ticker, 'at', stock.price, 'on', list(testing_prices[list(testing_prices.keys())[0]].keys())[pos])
                account.buy(stock, round(abs((MAX_TRANSACTION / stock.price) * math.sqrt(predictions[ticker][pos][0])), 3))
                sell_orders[str([int(inverse_time_effect3(MAX_HOLDING, predictions[ticker][pos][0])) + pos, ticker])] = [ticker, round(abs((MAX_TRANSACTION / stock.price) * math.sqrt(predictions[ticker][pos][0])), 3)]

        # Lets hope the same stock doesn't have two sell orders on the same day
        if str([pos, ticker]) in sell_orders.keys():
            account.sell(stocks[sell_orders[str([pos, ticker])][0]], sell_orders[str([pos, ticker])][1])
        net_worth.append(account.net_worth())
    return net_worth

def base_return(account, stocks, testing_prices, starting_market_cap, MAX_TRANSACTION):
    max_market_cap = max(starting_market_cap.values())
    for ticker in stocks.keys():
        to_spend = MAX_TRANSACTION * (starting_market_cap[ticker] / max_market_cap)
        stocks[ticker].update_price(testing_prices[ticker].iloc[0])
        account.buy(stocks[ticker], to_spend / stocks[ticker].price)

    initial = abs(account.balance)
    for ticker in stocks.keys():
        stocks[ticker].update_price(testing_prices[ticker].iloc[-1])

    return ((account.net_worth()) / initial) * 100
