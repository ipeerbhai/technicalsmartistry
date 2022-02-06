import cv2
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model
import numpy as np

## load the picture
pictureFile = "./RandomSmallPic.png" 
inputImage = cv2.imread(pictureFile) # 139*177*3 = 71421
inputTensor = tf.convert_to_tensor(inputImage, dtype=tf.float32)

## add dims to make the fits work
inputTensor = tf.expand_dims(inputTensor , 0)
inputTensor = tf.reshape(inputTensor, (73809,1))

## optional -- we can set a random seed
tf.random.set_seed(42)

## define a network
with tf.device('/CPU:0'):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(73809, input_shape=(73809,1), activation=None))

    model.compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=['mse']
    )

    model.fit(inputTensor, inputTensor, epochs=1, batch_size=1)

    ## This will throw an out of memory exception (OOM when allocating tensor with shape[32,73809])
    foo = model.predict([inputTensor])

    ## convert foo back to a picture and display
    
