import yfinance as yf
import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from util import *
from Mean_Reversion_Train import *
import os
import shutil


def test(MODEL_PATH, testing_prices, MAX_HOLDING=100):
    sma10 = get_sma(testing_prices, 10)
    sma30 = get_sma(testing_prices, 20)
    sma50 = get_sma(testing_prices, 50)
    sma100 = get_sma(testing_prices, 100)
    sd10 = get_sd(testing_prices, 10)
    sd30 = get_sd(testing_prices, 20)
    sd50 = get_sd(testing_prices, 50)
    sd100 = get_sd(testing_prices, 100)
    
    MAX_SMA = MAX_HOLDING
    x = []
    for pos in range(0, len(testing_prices) - MAX_SMA):
        x.append([sma10[pos], sma30[pos], sma50[pos], sma100[pos], sd10[pos], sd30[pos], sd50[pos], sd100[pos]])
    x = np.array(x)
    
    model = keras.models.load_model(MODEL_PATH)
    predictions = model.predict(x)

    average = round(float((sum(predictions) / len(predictions))[0]), 5)
    for pos in range(len(predictions)):
        predictions[pos] -= average

    to_normalize = max(abs(min(predictions)), abs(max(predictions)))
    for pos in range(len(predictions)):
        predictions[pos] /= to_normalize
    return predictions