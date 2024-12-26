def simple_trade(account, stocks, test_prices, p_outlook):
    MAX_TRANSACTION = 1000
    net_worth = []

    for pos in range(len(test_prices[list(test_prices.keys())[0]])):
        for ticker in stocks.keys():
            stock = stocks[ticker]

            stock.update_price(test_prices[ticker][pos])
            if p_outlook[ticker][pos] > 0.2:
                account.buy(stock, abs(round((MAX_TRANSACTION * p_outlook[ticker][pos]), 3)))
            elif p_outlook[ticker][pos] < -0.6:
                account.sell(stock, abs(round((MAX_TRANSACTION * p_outlook[ticker][pos]), 3)))

        net_worth.append(account.net_worth())
    return net_worth