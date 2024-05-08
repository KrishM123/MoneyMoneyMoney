import yfinance as yf
import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from util import *
from Mean_Reversion_Train import *
import os
import shutil


def test(model, testing_prices, MAX_HOLDING=100):
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

    predictions = model.predict(x)
    dates = testing_prices.keys()
    CONFIDENT_X = 10

    bests = [(float(predictions[x][0]), dates[0]) for x in range(CONFIDENT_X)]
    worsts = [(float(predictions[x][0]), dates[0]) for x in range(CONFIDENT_X)]

    for pred_pos in range(len(predictions[CONFIDENT_X:])):
        val = predictions[CONFIDENT_X:][pred_pos]
        min_bests = 100
        max_worsts = -100        
        for pos in range(CONFIDENT_X):
            if bests[pos][0] < min_bests:
                min_pos = pos
                min_bests = bests[pos][0]
            if worsts[pos][0] > max_worsts:
                max_pos = pos
                max_worsts = worsts[pos][0]
        
        if float(val[0]) > min_bests:
            bests.pop(min_pos)
            bests.append((float(val[0]), dates[pred_pos]))
        if float(val[0]) < max_worsts:
            worsts.pop(max_pos)
            worsts.append((float(val[0]), dates[pred_pos]))
    
    suggestions = []
    for ele in bests:
        suggestions.append({"datetime": str(ele[1])
                            , "confidence": abs(ele[0])
                            , "suggestion": "Buy"})
    for ele in worsts:
        suggestions.append({"datetime": str(ele[1])
                            , "confidence": abs(ele[0])
                            , "suggestion": "Sell"})
    return suggestions