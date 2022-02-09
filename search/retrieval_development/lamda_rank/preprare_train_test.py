import pandas as pd
import numpy as np
from search.retrieval_development.functions import df_transform

train = pd.read_csv("data/train.txt", header=None, sep=" ")

# have a look at first 5 rows

print(train.head())

# Each row is a query - document pair
# Column 0 is an integer - values 0-4 for relevancy
# Column 1 is an integer identifying the query
# Everything else holds the feature values, but the last column
# Last column is 'nan' and comes from how we split  the data

train_df = df_transform(train)

print(train_df.sample(3))

test = pd.read_csv("data/test.txt", header=None, sep=" ")
test_df = df_transform(test)

print(test_df.sample(3))

# Column 0 is the y label, queryid = column 0 ==> rest are features

# Saving the data sets to be able to load them quickly

train_df.to_pickle('data/train.pkl')
test_df.to_pickle('data/test.pkl')
