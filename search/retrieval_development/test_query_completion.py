# https://machinelearningmastery.com/text-generation-lstm-recurrent-neural-networks-python-keras/

import numpy
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
import xml.etree.ElementTree as ET
from preprocessing import Preprocessing
from functions import create_doc_dictionary
import pickle


def unpickle(filename):
    with open(filename, "rb") as fp:
        file_to_return = pickle.load(fp)
    return file_to_return


def pickle_file(dump_file, filename):
    with open(filename, "wb") as fp:
        pickle.dump(dump_file, fp)


# preprocessor = Preprocessing()
# filename = "trec.5000.xml"
# tree = ET.parse(filename)
# document_dic = create_doc_dictionary(tree, preprocessor)
# raw_text = list(document_dic.values())
# all_raw_text = []
# for entry in raw_text:
#     for element in entry:
#         for character in element:
#             all_raw_text.append(character)
#
# pickle_file(all_raw_text, "all_raw_text")
# chars = sorted(list(set(all_raw_text)))
#
pickle_filename = "pickle_test"
#
# pickle_file(chars, pickle_filename)

chars = unpickle(pickle_filename)
raw_text = unpickle("all_raw_text")
chars_to_int = dict((c, i) for i, c in enumerate(chars))  # mapping each character to an integer

n_chars = len(raw_text)
n_vocab = len(chars)
print("Total Characters: ", n_chars)
print("Total Vocab: ", n_vocab)

seq_length = 100
dataX = []
dataY = []
for i in range(0, n_chars - seq_length, 1):
    seq_in = raw_text[i:1 + seq_length]
    seq_out = raw_text[i + seq_length]
    dataX.append([chars_to_int[char] for char in seq_in])
    dataY.append(chars_to_int[seq_out])
n_patterns = len(dataX)
print("Total Patterns: ", n_patterns)

# Now that we have prepared training data, we need to transform it so that it is suitable with Keras

# Reshape X to be [samples, time steps, features]
X = numpy.reshape(dataX, (n_patterns, seq_length, 1))
# Normalize
X = X / float(n_vocab)
# One Hot Encode the output variable
y = np_utils.to_categorical(dataY)

# The problem is really a single character classification problem with 47 classes and as such is defined as
# optimizing the log loss (cross entropy), using ADAM optimization algo for speed

model = Sequential()
model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2])))
model.add(Dropout(0.2))
model.add(Dense(y.shape[1], activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')


# Network is sloew to train ==> model checkpointing to record all of the network weights to file each time
# an improvement in loss is observed at the end of an epoch
# We will use the best set of weights to instantiate our generative model in the next section.

# define the checkpoint
filepath="weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
callbacks_list = [checkpoint]

model.fit(X, y, epochs=20, batch_size=128, callbacks=callbacks_list)