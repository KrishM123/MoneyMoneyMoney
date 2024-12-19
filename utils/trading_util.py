import os
import json
import requests

class Account:
    def __init__(self):
        self.balance = 0
        self.holdings = {}
        self.min_balance = 0

    def buy(self, stock, quantity):
        cost = stock.price * quantity
        self.balance -= cost
        self.min_balance = min(self.balance, self.min_balance)
        self.holdings[stock] = self.holdings.get(stock, 0) + quantity
        stock.add_holding(quantity)

    def sell(self, stock, quantity):
        self.balance += stock.price * quantity
        self.holdings[stock] = self.holdings.get(stock, 0) - quantity
        stock.remove_holding(quantity)

    def net_worth(self):
        total_stock_value = sum(stock.price * quantity for stock, quantity in self.holdings.items())
        return self.balance + total_stock_value

    def profit(self):
        if self.min_balance == 0:
            return 0.0
        return (self.net_worth() / abs(self.min_balance)) * 100

    def __str__(self):
        holdings_str = "\n".join([f"{stock.name}: {quantity} shares" for stock, quantity in self.holdings.items()])
        return (
            f"Balance: ${self.balance:.2f}\n"
            f"Net Worth: ${self.net_worth():.2f}\n"
            f"Total Profit: {self.profit():.2f}%\n"
            f"Holdings:\n{holdings_str}"
        )


class Stock:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.holding = 0

    def update_price(self, new_price):
        self.price = new_price

    def add_holding(self, quantity):
        self.holding += quantity

    def remove_holding(self, quantity):
        self.holding -= quantity


def parse_snp_tickers():
    table = open('slickcharts.txt', 'r').read().split('<th scope="col">% Chg</th>')[1].split('</tbody>')[0].split('<tbody>')[1].split('<tr>')[1:]
    tickers = [x.split('/symbol/')[1].split('"')[0].replace(".", "-") for x in table]

    with open('snp.json', 'w') as f:
        json.dump(tickers, f)

    
def get_market_cap(START_DATE, tickers):
    START_DATE = START_DATE.strftime("%Y-%m-%d")
    load_dotenv()
    api_key1 = os.getenv('FMP_API_KEY1')
    api_key2 = os.getenv('FMP_API_KEY2')
    api_key3 = os.getenv('FMP_API_KEY3')
    api_key4 = os.getenv('FMP_API_KEY4')
    api_key5 = os.getenv('FMP_API_KEY5')
    api_key6 = os.getenv('FMP_API_KEY6')

    url = f'https://financialmodelingprep.com/api/v3/historical-market-capitalization/'


    market_cap = {}
    
    api = api_key1
    print('Using api key 1 to get market cap')
    for ticker in tickers:
        response = requests.get(url + f'{ticker}?&from={START_DATE}&apikey={api}').json()
        while ("Error Message" in response):
            if api == api_key1:
                print("Using api key 2 to get market cap")
                api = api_key2
            elif api == api_key2:
                print("Using api key 3 to get market cap")
                api = api_key3
            elif api == api_key3:
                print("Using api key 4 to get market cap")
                api = api_key4
            elif api == api_key4:
                print("Using api key 5 to get market cap")
                api = api_key5
            elif api == api_key5:
                print("Using api key 6 to get market cap")
                api = api_key6
            response = requests.get(url + f'{ticker}?&from={START_DATE}&apikey={api}').json()
        market_cap[ticker] = [int(x['marketCap']) for x in response]

    with open('data/market_cap.json', 'w') as f:
        json.dump(market_cap, f)


def base_index_return(stocks, market_cap, testing_prices):
    if len(stocks) == 1:
        return ((testing_prices[list(stocks.keys())[0]].iloc[-1] - testing_prices[list(stocks.keys())[0]].iloc[0]) / testing_prices[list(stocks.keys())[0]].iloc[0]) * 100
    final = sum([market_cap[ticker][0] for ticker in stocks.keys()])
    initial = sum([market_cap[ticker][-1] for ticker in stocks.keys()])
    return ((final - initial) / initial) * 100


def base_return(testing_prices):
    trade_volume = 500
    final = sum([((testing_prices[ticker].iloc[-1] * trade_volume) / testing_prices[ticker].iloc[0]) for ticker in testing_prices.keys()])
    initial = trade_volume * len(testing_prices)
    return ((final - initial) / initial) * 100