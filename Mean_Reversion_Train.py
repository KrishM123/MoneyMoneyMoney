import yfinance as yf
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from util import *
import os
import shutil

def create_model():
    return tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(8,), name='layers_flatten'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1),
    ])


def find_answers(prices, MAX_HOLDING):
    answer = []
    for pos1 in range(len(prices) - MAX_HOLDING):
        ans = 0
        for pos2 in range(1, MAX_HOLDING):
            ans += (prices.iloc[pos1 + pos2] - prices.iloc[pos1]) * time_effect1(MAX_HOLDING, pos2)
        answer.append(ans)

    dp_factors = [answer[0]]
    for pos in range(1, len(answer)):
        dp_factors.append(max(abs(answer[pos]), abs(dp_factors[-1])))
        answer[pos] /= dp_factors[pos]
    answer[0] = 1
    return answer


time_effect1 = lambda L, x: 1-(x/L)
time_effect2 = lambda L, x: L/(x+L)
time_effect3 = lambda L, x: (-1/(L**2))(x**2)+1
time_effect3 = lambda L, x: -1/((x-L)**2)


def train(save_name, training_prices, MAX_HOLDING=100, LONGEST_SMA=100):
    answer = find_answers(training_prices, MAX_HOLDING)

    sma10 = get_sma(training_prices, 10)
    sma30 = get_sma(training_prices, 20)
    sma50 = get_sma(training_prices, 50)
    sma100 = get_sma(training_prices, 100)
    sd10 = get_sd(training_prices, 10)
    sd30 = get_sd(training_prices, 20)
    sd50 = get_sd(training_prices, 50)
    sd100 = get_sd(training_prices, 100)

    if MAX_HOLDING < LONGEST_SMA:
        answer = answer[LONGEST_SMA - MAX_HOLDING:]

    x = []
    y = []
    for pos in range(0, len(training_prices) - LONGEST_SMA):
        x.append([sma10[pos], sma30[pos], sma50[pos], sma100[pos], sd10[pos], sd30[pos], sd50[pos], sd100[pos]])
        ans = (answer[pos] + 1) / 2
        y.append(ans)
    x = np.array(x)
    y = np.array(y)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

    model = create_model()
    model.compile(optimizer='adam',
                loss='mean_absolute_error',)
    model.fit(x=x_train, 
            y=y_train, 
            epochs=50, 
            validation_data=(x_test, y_test), 
    )
    
    if not os.path.exists(save_name):
        os.makedirs(save_name)
    else:
        shutil.rmtree(save_name)
        os.makedirs(save_name)
    model.save(save_name)
    model.save_weights(save_name)