import pandas as pd

train_df = pd.read_pickle("data/train.pkl")
test_df = pd.read_pickle("data/test.pkl")

train_df = train_df.sort_values(1)
train_df.head()

train_grp = train_df[1]  # query ids
train_truth = train_df[0]  # relevancy
train_X = train_df.loc[:, 2:]  # extracting all features
