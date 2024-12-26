import os
import json
import requests
from dotenv import load_dotenv
import sys

class Account:
    """
    Represents a trading account with a balance, holdings, and methods for buying, 
    selling, calculating net worth, and tracking profit over time.
    """
    def __init__(self):
        """
        Initializes the account with a zero balance, no holdings, and no minimum balance.
        """
        self.balance = 0
        self.holdings = {}
        self.min_balance = 0

    def buy(self, stock, quantity):
        """
        Buys a specified quantity of a stock, updating the account balance and holdings.
        
        Args:
            stock: Stock object, the stock to purchase.
            quantity: int, the number of shares to buy.
        """
        cost = stock.price * quantity
        self.balance -= cost
        self.min_balance = min(self.balance, self.min_balance)
        if stock not in self.holdings:
            self.holdings[stock] = 0
        self.holdings[stock] += quantity
        stock.add_holding(quantity)

    def sell(self, stock, quantity):
        """
        Sells a specified quantity of a stock, updating the account balance and holdings.
        
        Args:
            stock: Stock object, the stock to sell.
            quantity: int, the number of shares to sell.
        """
        revenue = stock.price * quantity
        self.balance += revenue
        if stock not in self.holdings:
            self.holdings[stock] = 0
        self.holdings[stock] -= quantity
        stock.remove_holding(quantity)

    def net_worth(self):
        """
        Calculates the net worth of the account, including balance and stock holdings.
        
        Returns:
            float, the total net worth of the account.
        """
        total_stock_value = sum(stock.price * quantity for stock, quantity in self.holdings.items())
        return self.balance + total_stock_value

    def profit(self):
        """
        Calculates the profit percentage relative to the minimum balance.
        
        Returns:
            float, the profit percentage. Returns 0.0 if the minimum balance is zero.
        """
        if self.min_balance == 0:
            return 0.0
        return (self.net_worth() / abs(self.min_balance)) * 100

    def __str__(self):
        """
        Returns a string representation of the account's balance, net worth, profit, and holdings.
        
        Returns:
            str, the string representation of the account details.
        """
        holdings_str = "\n".join([f"{stock.name}: {quantity} shares" for stock, quantity in self.holdings.items()])
        return (
            f"Balance: ${float(self.balance):.2f}\n" +
            f"Net Worth: ${float(self.net_worth()):.2f}\n" +
            f"Total Profit: {float(self.profit()):.2f}%\n" +
            f"Holdings:\n{holdings_str}"
        )

class Stock:
    """
    Represents a stock with a name, current price, and holding quantity.
    """
    def __init__(self, name, price):
        """
        Initializes a stock with a name, price, and zero holdings.
        
        Args:
            name: str, the name of the stock.
            price: float, the current price of the stock.
        """
        self.name = name
        self.price = price
        self.holding = 0

    def update_price(self, new_price):
        """
        Updates the stock price.
        
        Args:
            new_price: float, the new price of the stock.
        """
        self.price = new_price

    def add_holding(self, quantity):
        """
        Adds a specified quantity to the stock's holdings.
        
        Args:
            quantity: int, the number of shares to add.
        """
        self.holding += quantity

    def remove_holding(self, quantity):
        """
        Removes a specified quantity from the stock's holdings.
        
        Args:
            quantity: int, the number of shares to remove.
        """
        self.holding -= quantity

def parse_snp_tickers():
    """
    Parses S&P 500 tickers from a local HTML file and saves them to a JSON file.
    """
    table = open('slickcharts.txt', 'r').read().split('<th scope="col">% Chg</th>')[1].split('</tbody>')[0].split('<tbody>')[1].split('<tr>')[1:]
    tickers = [x.split('/symbol/')[1].split('"')[0].replace(".", "-") for x in table]

    with open('snp.json', 'w') as f:
        json.dump(tickers, f)

def get_market_cap(path, START_DATE, tickers):
    """
    Retrieves historical market capitalization data for specified tickers from a given start date.
    
    Args:
        path: str, the file path to save the market cap data as JSON.
        START_DATE: datetime, the start date for historical data retrieval.
        tickers: list of str, the stock tickers to retrieve market cap data for.
        
    Returns:
        dict, market capitalization data keyed by ticker.
    """
    START_DATE = START_DATE.strftime("%Y-%m-%d")
    sys.path.append(os.path.abspath('../'))
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
        while "Error Message" in response:
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

def base_index_return(market_cap, min_balance):
    """
    Calculates the base index return based on market capitalization changes over time.
    
    Args:
        market_cap: dict, the market capitalization data keyed by ticker.
        min_balance: float, the initial balance used for scaling the index.
        
    Returns:
        list of float, the index return values over time.
    """
    index_values = []
    initial_total_market_cap = sum(market_cap[ticker][0] for ticker in market_cap.keys())
    num_time_steps = len(next(iter(market_cap.values())))
    for t in range(num_time_steps):
        total_market_cap = sum(market_cap[ticker][t] for ticker in market_cap.keys())
        index_value = (total_market_cap / initial_total_market_cap) * min_balance
        index_values.append(index_value - min_balance)
    return index_values

def base_return(testing_prices):
    """
    Calculates the base return for a set of testing prices assuming equal trade volume.
    
    Args:
        testing_prices: dict of pandas.DataFrame, historical price data keyed by ticker.
        
    Returns:
        float, the percentage return of the base portfolio.
    """
    trade_volume = 500
    final = sum([((testing_prices[ticker].iloc[-1] * trade_volume) / testing_prices[ticker].iloc[0]) for ticker in testing_prices.keys()])
    initial = trade_volume * len(testing_prices)
    return ((final - initial) / initial) * 100
