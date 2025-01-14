import math
import random
import numpy as np
from datetime import timedelta


def get_sma_sd_v(prices, FEATURE_KERNAL_SIZES, MAX_HISTORY):
    """
    Computes the simple moving average (SMA), standard deviation (SD), and volatility
    for price data using multiple kernel sizes. Returns a merged feature set containing
    SMA, SD, and volatility values for each window size and history length.
    
    Args:
        prices: list of float, the input price data series.
        FEATURE_KERNAL_SIZES: list of int, kernel sizes for calculating SMA, SD, and volatility.
        MAX_HISTORY: int, the maximum history length for feature computation.
        
    Returns:
        A list of lists representing merged features across all kernel sizes and history.
    """
    all_features = []
    for size in FEATURE_KERNAL_SIZES:
        size_features = []
        window = prices[max(FEATURE_KERNAL_SIZES) - size:max(FEATURE_KERNAL_SIZES)]
        total = sum(window)
        mean = total / size
        sma = [mean]

        nume_sd_window = [(x-mean)**2 for x in window]
        nume_sd = sum(nume_sd_window)
        ind_sd = math.sqrt(nume_sd / size)
        sd = [(prices[max(FEATURE_KERNAL_SIZES) - 1] - mean) / ind_sd]

        volatility = [ind_sd * math.sqrt(size)]

        for pos1 in range(max(FEATURE_KERNAL_SIZES), len(prices)):
            window.append(prices[pos1])
            total += window[-1] - window[0]
            window = window[1:]
            mean = total / size
            sma.append(float(mean))

            nume_sd_window.append((prices[pos1] - mean) ** 2)
            nume_sd += nume_sd_window[-1] - nume_sd_window[0]
            nume_sd_window = nume_sd_window[1:]
            ind_sd = math.sqrt(nume_sd / size)
            sd.append(float((prices[pos1] - mean) / ind_sd))

            volatility.append(float(ind_sd * math.sqrt(size)))

            if len(sma) == MAX_HISTORY:
                size_features.append(normalize_start(sma) + normalize_start(sd) + normalize_start(volatility))
                sma.pop(0)
                sd.pop(0)
                volatility.pop(0)
        all_features.append(size_features)

    t_feat = transpose(all_features)
    merged = [[item for col in row for item in col] for row in t_feat]

    return merged

def normalize_start(numbers):
    """
    Normalizes a list of numbers to a scale of 1 to 100.
    If the first number is 0, it's treated as 1 for relative scaling.
    
    Args:
        numbers (list): List of numerical values
        
    Returns:
        list: Normalized list where values are scaled between 1 and 100
        
    Example:
        normalize([50, 100, 0]) returns [50, 100, 1]
        normalize([0, 50, 100]) returns [1, 50, 100]
    """
    if not numbers:
        return []
    
    first_number = numbers[0]
    if first_number == 0:
        first_number = 1
        
    relative_numbers = [num / first_number for num in numbers]
    
    min_val = min(relative_numbers)
    max_val = max(relative_numbers)
    
    def scale_to_range(x):
        if x == min_val:
            return 1
        elif x == max_val:
            return 100
        else:
            return 1 + (x - min_val) * (99) / (max_val - min_val)
    
    return [scale_to_range(x) for x in relative_numbers]


def transpose(matrix):
    """
    Transposes a 2D matrix, converting rows to columns and columns to rows.
    
    Args:
        matrix: list of list, the input matrix to transpose.
        
    Returns:
        A list of list representing the transposed matrix.
    """
    return [[matrix[col_pos][row_pos] for col_pos in range(len(matrix))] for row_pos in range(len(matrix[0]))]


def normalize_forward(data):
    """
    Normalizes data using forward scaling to ensure each element is scaled 
    relative to the maximum absolute value encountered up to that point.
    
    Args:
        data: list of float, the input data to normalize.
        
    Returns:
        A list of float representing the forward normalized data.
    """
    new_data = data.copy()
    dp_factors = [new_data[0]]
    for pos in range(1, len(new_data)):
        dp_factors.append(max(abs(new_data[pos]), abs(dp_factors[-1])))
        new_data[pos] /= dp_factors[pos]
    new_data[0] = 1
    return new_data


def normalize_average(data, kernal_size):
    """
    Normalizes data by dividing each value by the maximum value in a moving window 
    of specified kernel size.
    
    Args:
        data: list of float, the input data to normalize.
        kernal_size: int, the size of the moving window for normalization.
        
    Returns:
        A list of float representing the average normalized data.
    """
    new_data = data.copy()
    window = [abs(x) for x in new_data[:int(kernal_size/2)]]
    max_answer = max(window)
    dp_max = [max_answer] * int(kernal_size/2)
    for pos in range(int(kernal_size/2), len(new_data)):
        if len(window) == kernal_size:
            if max_answer == window[0]:
                max_answer = max(window[1:])
            window.pop(0)
        window.append(abs(new_data[pos]))
        max_answer = max(max_answer, abs(new_data[pos]))
        dp_max.append(abs(max_answer))
    for pos in range(len(new_data)):
        new_data[pos] /= dp_max[pos]
    return new_data


def gaussian_blur(data, sd):
    """
    Applies Gaussian blur to smooth the input data using a normal distribution 
    with specified standard deviation.
    
    Args:
        data: list of float, the input data to blur.
        sd: int, the standard deviation for the Gaussian function.
        
    Returns:
        A list of float representing the blurred data.
    """
    blurred_data = []
    for mean_pos in range(len(data)):
        total = data[mean_pos] * normal_distro(sd, 0)
        to_div = normal_distro(sd, 0)
        for pos in range(-(sd * 3),  (sd * 3) + 1):
            if mean_pos + pos > 0 and mean_pos + pos < len(data):
                total += data[mean_pos + pos] * normal_distro(sd, pos)
                to_div += normal_distro(sd, pos)
        blurred_data.append(total * (1 / to_div))
    return blurred_data


def gaussian_randomize(data, sd):
    """
    Randomizes data using a Gaussian distribution centered on each value 
    with a standard deviation proportional to the value.
    
    Args:
        data: list of float, the input data to randomize.
        sd: float, the standard deviation scaling factor for randomization.
        
    Returns:
        A list of float representing the randomized data.
    """
    randomized_data = []
    for value in data:
        randomized_value = random.gauss(value, sd * value)
        randomized_data.append(randomized_value)
    return randomized_data


def get_outlook(prices, MAX_HOLDING, TIME_EFFECT):
    """
    Computes a future outlook for prices based on weighted time effects 
    over a maximum holding period.
    
    Args:
        prices: list of float, the input price data series.
        MAX_HOLDING: int, the maximum holding period for calculating outlook.
        TIME_EFFECT: int, the key for selecting a specific time effect function.
        
    Returns:
        A list of float representing the computed outlook values.
    """
    outlook = []
    for pos1 in range(len(prices) - MAX_HOLDING):
        ans = 0
        for pos2 in range(1, MAX_HOLDING):
            ans += (prices[pos1 + pos2] - prices[pos1]) * time_effect[TIME_EFFECT](MAX_HOLDING, pos2)
        outlook.append(ans / time_effect_integrals[TIME_EFFECT](MAX_HOLDING))


def get_optimal_hold(prices, n_outlook, MAX_HOLDING, TIME_EFFECT):
    """
    Determines the optimal hold time for maximizing or minimizing gains based on 
    price movements and time-weighted effects over a given holding period.
    
    Args:
        prices: list of float, the input price data series.
        n_outlook: list of float, the outlook values for each time step.
        MAX_HOLDING: int, the maximum holding period for calculating optimal hold.
        TIME_EFFECT: int, the key for selecting a specific time effect function.
        
    Returns:
        A list of float representing the optimal holding times as fractions of MAX_HOLDING.
    """
    sell_time = []
    for day in range(len(prices) - MAX_HOLDING):
        if n_outlook[day] > 0:
            highest = 0
            highest_pos = 0
            for delay in range(MAX_HOLDING):
                delta = (prices[day + delay] - prices[day]) * time_effect[TIME_EFFECT](MAX_HOLDING, delay)
                if delta > highest:
                    highest = delta
                    highest_pos = delay
            sell_time.append(highest_pos / MAX_HOLDING)
        else:
            lowest = 0
            lowest_pos = 0
            for delay in range(MAX_HOLDING):
                delta = (prices[day + delay] - prices[day]) * time_effect[TIME_EFFECT](MAX_HOLDING, delay)
                if delta < lowest:
                    lowest = delta
                    lowest_pos = delay
            sell_time.append(lowest_pos / MAX_HOLDING)


def calculate_sharpe_ratio(portfolio_values, min_balance, risk_free_rate=0.0, periods_per_year=252):
    """
    Calculate the Sharpe Ratio for a strategy, handling cases where portfolio starts at 0.

    Parameters:
        portfolio_values (list or np.array): List of portfolio net worth values over time.
        risk_free_rate (float): Annual risk-free rate as a decimal (default is 0.0).
        periods_per_year (int): Number of periods per year (default is 252 for daily data).

    Returns:
        float: Sharpe Ratio of the strategy.
    """
    portfolio_values = np.array(portfolio_values) + abs(min_balance)
    
    returns = np.diff(portfolio_values) / portfolio_values[:-1]
    
    risk_free_rate_daily = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess_returns = returns - risk_free_rate_daily

    mean_excess_return = np.mean(excess_returns)
    std_deviation = np.std(excess_returns)

    sharpe_ratio = mean_excess_return / std_deviation
    sharpe_ratio_annualized = sharpe_ratio * np.sqrt(periods_per_year)

    return sharpe_ratio_annualized


# desmos.com/calculator/llzxki7h2o
time_effect = {
    1: lambda N, x: 1-(x/N),
    2: lambda N, x: -((x**2)/(N**2))+1,
    3: lambda N, x: ((x/N)-1) ** 2,
    4: lambda N, x: math.pow(math.e, -((math.log(1000))/(N^2)) * x**2)
}

time_effect_integrals = {
    1: lambda N: N/2,
    2: lambda N: (2*N)/3,
    3: lambda N: N/3,
    4: lambda N: (
        (math.sqrt(math.pi) * N) /
        (2 * math.sqrt(math.log(100)))
    ) * math.erf(math.sqrt(math.log(100)))
}


normal_distro = lambda s, x: (1/(s * math.sqrt(2 * math.pi))) * (math.e ** ((-1/2) * ((x/s) ** 2)))


def get_atm_iv(ticker, date):
    stock_price = ticker.history(start=date, end=date + timedelta(days=1))['Close'].iloc[0]
    options = ticker.option_chain(ticker.options[0])
    atm_call = options.calls.iloc[(options.calls['strike'] - stock_price).abs().argsort()[:1]]
    return atm_call['impliedVolatility'].values[0]
