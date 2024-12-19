import math
import random

def get_sma_sd_v(prices, window_sizes, MAX_FEATURE_KERNEL):
    all_features = []
    for size in window_sizes:
        window = prices[MAX_FEATURE_KERNEL - size:MAX_FEATURE_KERNEL]
        total = sum(window)
        mean = total / size
        sma = [mean]

        nume_sd_window = [(x-mean)**2 for x in window]
        nume_sd = sum(nume_sd_window)
        ind_sd = math.sqrt(nume_sd / size)
        sd = [(prices[MAX_FEATURE_KERNEL - 1] - mean) / ind_sd]

        volatility = [ind_sd * math.sqrt(size)]

        for pos1 in range(MAX_FEATURE_KERNEL, len(prices)):
            window.append(prices[pos1])
            total += window[-1] - window[0]
            window = window[1:]
            mean = total / size
            sma.append(mean)

            nume_sd_window.append((prices[pos1] - mean) ** 2)
            nume_sd += nume_sd_window[-1] - nume_sd_window[0]
            nume_sd_window = nume_sd_window[1:]
            ind_sd = math.sqrt(nume_sd / size)
            sd.append((prices[pos1] - mean) / ind_sd)

            volatility.append(ind_sd * math.sqrt(size))
        all_features.append(sma)
        all_features.append(sd)
        all_features.append(volatility)
    return all_features

def transpose(matrix):
    return [[matrix[col_pos][row_pos] for col_pos in range(len(matrix))] for row_pos in range(len(matrix[0]))]

def normalize_forward(data):
    new_data = data.copy()
    dp_factors = [new_data[0]]
    for pos in range(1, len(new_data)):
        dp_factors.append(max(abs(new_data[pos]), abs(dp_factors[-1])))
        new_data[pos] /= dp_factors[pos]
    new_data[0] = 1
    return new_data

def normalize_average(data, kernal_size):
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
    randomized_data = []
    for value in data:
        randomized_value = random.gauss(value, sd * value)
        randomized_data.append(randomized_value)
    return randomized_data

def get_outlook(prices, MAX_HOLDING, TIME_EFFECT):
    outlook = []
    for pos1 in range(len(prices) - MAX_HOLDING):
        ans = 0
        for pos2 in range(1, MAX_HOLDING):
            ans += (prices[pos1 + pos2] - prices[pos1]) * time_effect[TIME_EFFECT](MAX_HOLDING, pos2)
        outlook.append(ans / integrated_time_effect[TIME_EFFECT])

def get_optimal_hold(prices, n_outlook, MAX_HOLDING, TIME_EFFECT):
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

# https://www.desmos.com/calculator/jjttvu31pl
time_effect = {
    1: lambda L, x: 1-(x/L),
    2: lambda L, x: L/(x+L),
    3: lambda L, x: -((x**2)/(L**2))+1,
    4: lambda L, x: ((x/L)-1) ** 2
}

integrated_time_effect = {
    1: 50,
    2: -100 * math.log(100) + 100 * math.log(200),
    3: 200 / 3,
    4: 100 / 3
}

# https://www.desmos.com/calculator/jy32nucdmo
inverse_time_effect = {
    1: lambda L, x: L * x,
    2: lambda L, x: L - (L / (1 + x)),
    3: lambda L, x: L * (x ** 2),
    4: lambda L, x: -L * (x) * (x-2)
}

normal_distro = lambda s, x: (1/(s * math.sqrt(2 * math.pi))) * (math.e ** ((-1/2) * ((x/s) ** 2)))