from Mean_Reversion_Test import *
from Mean_Reversion_Train import *
from Trading_Strategies import *
import yfinance as yf
import matplotlib.pyplot as plt

snp_500_tickers = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "META", "BRK-B", "JPM", "JNJ", "V",
    "PG", "NVDA", "UNH", "HD", "DIS", "PYPL", "MA", "VZ", "ADBE", "NFLX",
    "CMCSA", "INTC", "KO", "PFE", "T", "PEP", "MRK", "ABBV", "ABT", "CSCO",
    "XOM", "ACN", "CRM", "AVGO", "NKE", "TMO", "MCD", "COST", "CVX", "TXN",
    "NEE", "MDT", "LLY", "UNP", "HON", "AMGN", "QCOM", "DHR", "LOW", "MS",
    "ORCL", "PM", "IBM", "BMY", "LIN", "RTX", "AMD", "SBUX", "INTU", "GS",
    "PLD", "AXP", "NOW", "BLK", "C", "ISRG", "MDLZ", "GE", "MMM", "AMT",
    "SYK", "LMT", "SPGI", "GILD", "CB", "MO", "BKNG", "CAT", "BA", "DE",
    "MU", "ZTS", "ADI", "CCI", "AMCR", "TFC", "FISV", "SCHW", "DUK", "EW",
    "SO", "USB", "ITW", "TGT", "CME", "CL", "MMC", "PNC", "CSX", "CI",
    "FDX", "APD", "BSX", "MET", "SHW", "HUM", "AON", "ADI", "REGN", "MNST",
    "EL", "ILMN", "ECL", "ROP", "ADP", "MAR", "ETN", "BK", "MRNA", "F",
    "GM", "SYY", "MCO", "KMB", "BAX", "SPG", "AEP", "CARR", "ROP", "PSA",
    "CTAS", "ADSK", "NSC", "EXC", "TRV", "STZ", "AIG", "TDG", "APH", "WMB",
    "ADM", "AFL", "A", "ANSS", "HLT", "VRSK", "RMD", "AWK", "MTD", "CTSH",
    "FTNT", "WEC", "SBAC", "MSI", "CNC", "LHX", "RSG", "PGR", "TT", "YUM",
    "WBA", "KMI", "KR", "OXY", "AVB", "CDW", "D", "VLO", "MKTX", "BIO",
    "CAG", "EBAY", "FMC", "CINF", "CMS", "HSY", "IP", "K", "KEY", "LUV",
    "LVS", "MPC", "NUE", "PPL", "RL", "SJM", "SLB", "STT", "SWKS", "TSN",
    "UHS", "VFC", "WAB", "WDC", "WELL", "XEL", "XYL", "ZBH"
]

historic_price = {}

for ticker in snp_500_tickers:
    historic_price[ticker] = yf.download(ticker)['Adj Close']


TRAIN_DATE = '2022-01-01'
MAX_HOLDING = 100

# for TICKER in historic_price.keys():
#     training_prices = historic_price[TICKER][:TRAIN_DATE]
#     testing_prices = historic_price[TICKER][TRAIN_DATE:]
#     train("Models/" + TICKER + "_" + TRAIN_DATE + ".keras", training_prices)


predictions = {}
testing_prices = {}
for TICKER in historic_price.keys():
    testing_prices[TICKER] = historic_price[TICKER][TRAIN_DATE:]
    predictions[TICKER] = test("Models/" + TICKER + "_" + TRAIN_DATE + ".keras", testing_prices[TICKER])
    testing_prices[TICKER] = testing_prices[TICKER][MAX_HOLDING:]


MAX_TRANSACTION = 10000
ACCOUNT_BALANCE = 500000
account = Account(ACCOUNT_BALANCE)
stocks = {}
for TICKER in historic_price.keys():
    stocks[TICKER] = Stock(TICKER, testing_prices[0])


for date in testing_prices['AAPL'].keys():
    
    net_worth, min_balance = confidence_as_duration(MAX_HOLDING, MAX_TRANSACTION, account, stocks, testing_prices, predictions)


plt.plot(testing_prices.keys(), net_worth)
plt.show()