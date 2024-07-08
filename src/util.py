import math
import json
import requests
from dotenv import load_dotenv
import os

def get_sma(prices, MA):
    sma = []
    for pos1 in range(0, len(prices) - MA):
        sum = 0
        for change in range(MA, 0, -1):
            sum += prices.iloc[pos1 + change]
        sma.append(sum / MA)
    return sma

def get_sd(prices, time):
    sd = []
    for pos1 in range(0, len(prices) - time):
        sum = 0
        for change in range(time, 0, -1):
            sum += prices.iloc[pos1 + change]
        mean = sum / time
        summa = 0
        for change in range(time, 0, -1):
            summa += (prices.iloc[pos1 + change] - mean) ** 2
        sd.append(math.sqrt(summa / time))
    return sd

def normalize_forward(old_answer):
    answer = old_answer.copy()
    dp_factors = [answer[0]]
    for pos in range(1, len(answer)):
        dp_factors.append(max(abs(answer[pos]), abs(dp_factors[-1])))
        answer[pos] /= dp_factors[pos]
    answer[0] = 1
    return answer

def normalize_average(old_answer, MAX_HOLDING):
    answer = old_answer.copy()
    window = [abs(x) for x in answer[:int(MAX_HOLDING/2)]]
    max_answer = max(window)
    dp_max = [max_answer] * int(MAX_HOLDING/2)
    for pos in range(int(MAX_HOLDING/2), MAX_HOLDING):
        window.append(abs(answer[pos]))
        max_answer = max(max_answer, abs(answer[pos]))
        dp_max.append(abs(max_answer))
    for pos in range(MAX_HOLDING, len(answer)):
        if max_answer == window[0]:
            max_answer = max(window[1:])
        max_answer = max(max_answer, abs(answer[pos]))
        window.pop(0)
        window.append(abs(answer[pos]))
        dp_max.append(abs(max_answer))
    for pos in range(len(answer)):
        answer[pos] /= dp_max[pos]
    return answer

time_effect1 = lambda L, x: 1-(x/L)
time_effect2 = lambda L, x: L/(x+L)
time_effect3 = lambda L, x: (-1/(L**2))(x**2)+1
time_effect3 = lambda L, x: -1/((x-L)**2)

inverse_time_effect1 = lambda L, x: min(L, max(L(1-x), 0))
inverse_time_effect2 = lambda L, x: min(L, max((L/x) - L, 0))
inverse_time_effect3 = lambda L, x: L * (x ** 2)
inverse_time_effect4 = lambda L, x: min(max(L - math.sqrt((L**2) * x), 0), L)

class Account():
    def __init__(self):
        self.balance = 0
        self.holdings = []
        self.min_balance = 0


    def buy(self, stock, quantity):
        if stock not in self.holdings:
            self.holdings.append(stock)
        self.balance -= stock.price * quantity
        self.min_balance = min(self.balance, self.min_balance)
        stock.add_holding(quantity)

    def sell(self, stock, quantity):
        self.balance += stock.price * quantity
        stock.remove_holding(quantity)

    def net_worth(self):
        return self.balance + sum([(stock.price * stock.holding) for stock in self.holdings])

class Stock():
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