import numpy as np
import sys
import os

import tensorflow as tf
from sklearn.model_selection import train_test_split

sys.path.append(os.path.abspath('../'))

from utils.ml_util import *
from utils.trading_util import *

def train(MODEL_PATH, train_prices, FEATURE_KERNEL_SIZES, MAX_HOLDING):
    TIME_EFFECT = 3

    outlook = []
    for pos1 in range(len(train_prices) - MAX_HOLDING):
        ans = 0
        for pos2 in range(1, MAX_HOLDING):
            ans += (train_prices[pos1 + pos2] - train_prices[pos1]) * time_effect[TIME_EFFECT](MAX_HOLDING, pos2)
        outlook.append(ans / integrated_time_effect[TIME_EFFECT])
        
    n_outlook = normalize_average(outlook, MAX_HOLDING * 3)

    features = get_sma_sd_v(train_prices, FEATURE_KERNEL_SIZES, max(FEATURE_KERNEL_SIZES))
    for pos in range(len(features)):
        features[pos] = features[pos][:-MAX_HOLDING - 1]
    n_outlook = n_outlook[max(FEATURE_KERNEL_SIZES):]

    x = np.array(transpose(features))
    y = np.array(n_outlook)


    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

    def create_model():
        inputs = tf.keras.layers.Input(shape=(len(FEATURE_KERNEL_SIZES) * 3,))
        
        x = tf.keras.layers.Dense(256, activation='relu')(inputs)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        
        residual_1 = x
        x = tf.keras.layers.Dense(512, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Add()([x, residual_1])
        
        residual_2 = x
        x = tf.keras.layers.Dense(512, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Add()([x, residual_2])
        
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        
        outputs = tf.keras.layers.Dense(1, activation='tanh')(x)
        
        return tf.keras.models.Model(inputs, outputs)

    model = create_model()
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                loss='mean_absolute_error')

    model.fit(x=x_train, 
            y=y_train, 
            epochs=70, 
            validation_data=(x_test, y_test), 
        )

    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
    model.save(MODEL_PATH)