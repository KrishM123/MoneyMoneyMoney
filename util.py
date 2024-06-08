import math

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
