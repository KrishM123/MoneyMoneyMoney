from src.util import *


def trade_index_with_confidence_as_duration(MAX_HOLDING, MAX_TRANSACTION, account, stocks, testing_prices, predictions, verbose):
    net_worth = []
    sell_orders = {}
    cover_orders = {}

    for pos in range(len(testing_prices[list(testing_prices.keys())[0]].keys())):
        for ticker in stocks.keys():

            stocks[ticker].update_price(testing_prices[ticker].iloc[pos])

            stock = stocks[ticker]

            if float(predictions[ticker][pos][0]) > 0.8:
                if verbose:
                    print('Bought ', ticker, 'at', stock.price, 'on', list(testing_prices[list(testing_prices.keys())[0]].keys())[pos])
                account.buy(stock, round(abs((MAX_TRANSACTION / stock.price) * predictions[ticker][pos][0]), 3))
                sell_orders[str([int(inverse_time_effect3(MAX_HOLDING, predictions[ticker][pos][0])) + pos, ticker])] = [ticker, round(abs((MAX_TRANSACTION / stock.price) * math.sqrt(predictions[ticker][pos][0])), 3)]

            # elif float(predictions[ticker][pos][0]) < -0.95:
            #     if verbose:
            #         print('Shorted ', ticker, 'at', stock.price, 'on', list(testing_prices[list(testing_prices.keys())[0]].keys())[pos])
            #     account.sell(stock, round(abs((MAX_TRANSACTION / stock.price) * abs(predictions[ticker][pos][0])), 3))
            #     cover_orders[str([int(inverse_time_effect3(MAX_HOLDING, abs(predictions[ticker][pos][0]))) + pos, ticker])] = [ticker, round(abs((MAX_TRANSACTION / stock.price) * math.sqrt(abs(predictions[ticker][pos][0]))), 3)]

        # Lets hope the same stock doesn't have two sell or cover orders on the same day
        if str([pos, ticker]) in sell_orders.keys():
            account.sell(stocks[sell_orders[str([pos, ticker])][0]], sell_orders[str([pos, ticker])][1])
        if str([pos, ticker]) in cover_orders.keys():
            account.buy(stocks[cover_orders[str([pos, ticker])][0]], cover_orders[str([pos, ticker])][1])

        net_worth.append(account.net_worth())
    return net_worth