import numpy as np
import glob
import tensorflow as tf
import cv2

# global variables
TOTAL_HORSES_TRAIN = 1067
TOTAL_ZEBRAS_TRAIN = 1190
TOTAL_PIXELS_PIC = 196608
TOTAL_HORSES_TEST = 120
TOTAL_ZEBRAS_TEST = 140
UPDATES_NUMBER = 10000


def logistic_fun(z):
    return 1 / (1.0 + np.exp(-z))


def making_data_x_from_train():
    train_horses = glob.glob('horses vs zebras/train/horses/*.*')
    train_zebras = glob.glob('horses vs zebras/train/zebras/*.*')
    data_train_horses_ = np.array([[cv2.imread(horse)] for horse in train_horses])
    data_train_zebras_ = np.array([[cv2.imread(zebra)] for zebra in train_zebras])

    data_train_horses_flat = np.array([np.array(mat1.ravel()) for mat1 in data_train_horses_])
    data_train_zebras_flat = np.array([np.array(mat1.ravel()) for mat1 in data_train_zebras_])

    data_train_horses_flat = np.array([a / 255. for a in data_train_horses_flat])
    data_train_zebras_flat = np.array([a / 255. for a in data_train_zebras_flat])

    data_x_tr = np.concatenate([data_train_horses_flat, data_train_zebras_flat])
    return data_x_tr, data_train_horses_flat, data_train_zebras_flat


def making_data_y():
    horses = np.array([[1] for x in range(TOTAL_HORSES_TRAIN)])  # number of pics in train horses
    zebras = np.array([[0] for y in range(TOTAL_ZEBRAS_TRAIN)])  # number of pics in train zebras
    data_y_in = np.concatenate([horses, zebras])
    return data_y_in


def making_data_test():
    test_horses = glob.glob('horses vs zebras/test/horses/*.*')
    test_zebras = glob.glob('horses vs zebras/test/zebras/*.*')
    data_test_horses = np.array([[cv2.imread(horse)] for horse in test_horses])
    data_test_zebras = np.array([[cv2.imread(zebra)] for zebra in test_zebras])
    data_test_horses_flat_ = np.array([np.array(mat.ravel()) for mat in data_test_horses])
    data_test_zebras_flat_ = np.array([np.array(mat.ravel()) for mat in data_test_zebras])
    data_test_horses_flat_ = np.array([a / 255. for a in data_test_horses_flat_])
    data_test_zebras_flat_ = np.array([a / 255. for a in data_test_zebras_flat_])
    return data_test_horses_flat_, data_test_zebras_flat_


def print_train_result():
    sumH = 0
    for horse in data_train_horses:
        prediction = logistic_fun(np.matmul(np.array([horse]), sess.run(W)) + sess.run(b))[0][0]
        sumH += prediction

    horse_prediction_train = sumH / TOTAL_HORSES_TRAIN
    print("Prediction on horses pictures from train: ", horse_prediction_train)
    horses_train_error = 1 - horse_prediction_train

    sumZ = 0
    for zebra in data_train_zebras:
        prediction = logistic_fun(np.matmul(np.array([zebra]), sess.run(W)) + sess.run(b))[0][0]
        sumZ += prediction

    zebra_prediction_train = (sumZ / TOTAL_ZEBRAS_TRAIN)
    print("Prediction on zebras pictures from train: ", zebra_prediction_train)
    zebras_train_error = zebra_prediction_train

    print("train error: ", (horses_train_error + zebras_train_error) / 2.)


def print_test_results():
    (classify_as_horse_right, classify_as_zebra_wrong, classify_as_zebra_right, classify_as_horse_wrong) = (0, 0, 0, 0)
    sumH = 0
    for horse in data_test_horses_flat:
        prediction = logistic_fun(np.matmul(np.array([horse]), sess.run(W)) + sess.run(b))[0][0]
        sumH += prediction
        if (prediction > 0.5):
            classify_as_horse_right += 1
        else:
            classify_as_zebra_wrong += 1
    horse_prediction_test = sumH / TOTAL_HORSES_TEST
    print("\nPrediction on horses pictures from test: ", horse_prediction_test)
    horses_train_error = 1 - horse_prediction_test

    sumZ = 0
    for zebra in data_test_zebras_flat:
        prediction = logistic_fun(np.matmul(np.array([zebra]), sess.run(W)) + sess.run(b))[0][0]
        sumZ += prediction
        if (prediction < 0.5):
            classify_as_zebra_right += 1
        else:
            classify_as_horse_wrong += 1

    zebra_prediction_test = (sumZ / TOTAL_ZEBRAS_TEST)
    print("Prediction on zebras pictures from test: ", zebra_prediction_test)
    zebras_train_error = zebra_prediction_test

    accuracy = (classify_as_horse_right + classify_as_zebra_right) / (TOTAL_HORSES_TEST + TOTAL_HORSES_TEST)
    precision = classify_as_horse_right / (classify_as_horse_right + classify_as_horse_wrong)
    recall = classify_as_horse_right / TOTAL_HORSES_TEST
    test_error = ((1 - horse_prediction_test) + zebra_prediction_test) / 2.

    print('test error: %.4f ' % (test_error))
    print('\naccuracy: %.4f' % (accuracy))
    print('precision: %.4f ' % (precision))
    print('recall: %.4f ' % (recall))


features = TOTAL_PIXELS_PIC  # number of pixels in each pic
eps = 1e-12
x = tf.compat.v1.placeholder(tf.float32, [None, features])
y_ = tf.compat.v1.placeholder(tf.float32, [None, 1])
W = tf.Variable(tf.zeros([features, 1]))
b = tf.Variable(tf.zeros([1]))
y = 1 / (1.0 + tf.exp(-(tf.matmul(x, W) + b)))
loss1 = -(y_ * tf.math.log(y + eps) + (1 - y_) * tf.math.log(1 - y + eps))
loss = tf.reduce_mean(loss1)
update = tf.compat.v1.train.GradientDescentOptimizer(0.0001).minimize(loss)

(data_x, data_train_horses , data_train_zebras) = making_data_x_from_train()
data_y = making_data_y()
sess = tf.compat.v1.Session()
sess.run(tf.compat.v1.global_variables_initializer())
for i in range(0, UPDATES_NUMBER):
    sess.run(update, feed_dict={x: data_x, y_: data_y})  # BGD

print_train_result()

(data_test_horses_flat, data_test_zebras_flat) = making_data_test()

print_test_results()
