import os
import json
import requests

class Account:
    def __init__(self):
        self.balance = 0.0
        self.holdings = {}
        self.min_balance = 0.0

    def buy(self, stock, quantity):
        cost = float(stock.price * quantity)
        self.balance = float(self.balance - cost)
        self.min_balance = min(self.balance, self.min_balance)
        if stock not in self.holdings:
            self.holdings[stock] = 0
        self.holdings[stock] = self.holdings[stock] + quantity
        stock.add_holding(quantity)

    def sell(self, stock, quantity):
        revenue = float(stock.price * quantity)
        self.balance = float(self.balance + revenue)
        if stock not in self.holdings:
            self.holdings[stock] = 0
        self.holdings[stock] = self.holdings[stock] - quantity
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
            f"Balance: ${float(self.balance):.2f}\n" +
            f"Net Worth: ${float(self.net_worth()):.2f}\n" +
            f"Total Profit: {float(self.profit()):.2f}%\n" +
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

    
def get_market_cap(path, START_DATE, tickers):
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

    with open(path, 'w') as f:
        json.dump(market_cap, f)
    return market_cap


def base_index_return(stocks, market_cap):
    total_market_caps = [
        sum(market_cap[ticker][i] for ticker in stocks.keys())
        for i in range(len(next(iter(market_cap.values()))))
    ]
    
    base_value = total_market_caps[0]
    normalized_market_caps = [100 * (value / base_value) for value in total_market_caps]
    
    return normalized_market_caps


def base_return(testing_prices):
    trade_volume = 500
    final = sum([((testing_prices[ticker].iloc[-1] * trade_volume) / testing_prices[ticker].iloc[0]) for ticker in testing_prices.keys()])
    initial = trade_volume * len(testing_prices)
    return ((final - initial) / initial) * 100