from Mean_Reversion_Test import *
from Mean_Reversion_Train import *
import yfinance as yf
import matplotlib.pyplot as plt

TICKER = "SU"
historic_price = yf.download(TICKER)
prices = historic_price['Adj Close']['2005-01-01':]

TRAIN_DATE = '2022-01-01'
MAX_HOLDING = 100
training_prices = prices[:TRAIN_DATE]
testing_prices = prices[TRAIN_DATE:]

#train("Models/" + TICKER + "_" + TRAIN_DATE + ".keras", training_prices)
predictions = test("Models/" + TICKER + "_" + TRAIN_DATE + ".keras", testing_prices)
testing_prices = testing_prices[MAX_HOLDING:]

MAX_TRANSACTION = 5000
account = Account(100000)
nvda = Stock(TICKER, testing_prices[0])

net_worth = []
for pos in range(len(testing_prices)):
    nvda.update_price(testing_prices.iloc[pos])
    if float(predictions[pos][0]) > 0:
        account.buy(nvda, round(abs((MAX_TRANSACTION / nvda.price) * predictions[pos][0]), 3))
    elif float(predictions[pos][0]) < 0:
        account.sell(nvda, round(abs((MAX_TRANSACTION / nvda.price) * predictions[pos][0] * 2), 3))
    net_worth.append(account.net_worth())

plt.plot(testing_prices.keys(), net_worth)
plt.show()