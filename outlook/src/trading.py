def simple_trade(account, stocks, test_prices, p_outlook):
    MAX_TRANSACTION = 1000
    net_worth = []

    for pos in range(len(test_prices[list(test_prices.keys())[0]].keys())):
        for ticker in stocks.keys():

            stocks[ticker].update_price(test_prices[ticker][pos])

            stock = stocks[ticker]

            if p_outlook[ticker][pos] > 0.4:
                account.buy(stock, round((MAX_TRANSACTION * p_outlook[ticker][pos]), 3))
            elif p_outlook[ticker][pos] < 0.4:
                account.sell(stock, round((MAX_TRANSACTION * p_outlook[ticker][pos]), 3))

        net_worth.append(account.net_worth())
    return net_worth