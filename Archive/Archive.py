
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