import pandas as pd
import tensorflow as tf
import numpy as np
import sys
import os

sys.path.append(os.path.abspath('../'))

from utils.ml_util import *


def infer(MODEL_PATH, test_prices, FEATURE_KERNEL_SIZES, MAX_HISTORY):

    model = tf.keras.models.load_model(MODEL_PATH)

    features = get_sma_sd_v(test_prices, FEATURE_KERNEL_SIZES, MAX_HISTORY)

    x = np.array(features)

    p_outlook = model.predict(x)
    p_outlook = [x[0] for x in p_outlook]
    return p_outlook