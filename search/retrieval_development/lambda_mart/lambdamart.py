import pandas as pd
import xgboost as xgb
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


def get_D_matrix(df):
    """
    Function to create the DMatrix - internal data structure used by XGBoost,
    optimized for both memory efficiency and training speed
    Input: df
    Return: df
    """
    df = df.sort_values(1)
    grp = df[1]  # query ids
    grp_info = {}  # dictionary to store how many entries we have for each query
    for i in grp:
        if i in grp_info.keys():
            grp_info[i] = grp_info[i] + 1
        else:
            grp_info[i] = 1
    grp_info_counts = [grp_info[key] for key in grp_info]

    y = df[0]  # labels / relevancy values
    X = df.loc[:, 2:]  # extracts all features
    X.columns = ['x_' + str(x) for x in range(1, 137, 1)]
    X = X.apply(pd.to_numeric)
    df_DMatrix = xgb.DMatrix(X, label=y)  # Create the DMatrix which is pretty much a dataframe but optimised
    grp = grp.map(pd.to_numeric)
    df_DMatrix.set_group(grp_info_counts)
    print("Number of rows y label = " + str(len(grp)))
    print("Shape of X = " + str(len(X.shape)))
    return df_DMatrix


sns.set()

# Reading the path as 'data/train.pkl' did not work (not found) but the absolute path seems to work

train_df = pd.read_pickle(
    "/Users/vladmatei/PycharmProjects/TextTechnologiesDS/Search_engine/search/retrieval_development/data/train.pkl")
test_df = pd.read_pickle(
    "/Users/vladmatei/PycharmProjects/TextTechnologiesDS/Search_engine/search/retrieval_development/data/test.pkl")

train_data = get_D_matrix(train_df)
test_data = get_D_matrix(test_df)

# ### Using LambdaMart - combines LambdaRank and MART (Multiple Additive Regression Trees) ### On experimental data
# sets, LambdaMART has shown better results than LambdaRank and the original RankNet ###
# https://medium.com/@nikhilbd/intuitive-explanation-of-learning-to-rank-and-ranknet-lambdarank-and-lambdamart
# -fe1e17fac418

model_params = {'objective': 'rank:pairwise', 'learning_rate': 0.1, 'gama': 1.0, 'min_child_weight': 0.1,
                'max_depth': 4, 'n_estimators': 10,
                'eval_metric': ['ndcg@1', 'ndcg@5', 'ndcg@10', 'ndcg@20', 'ndcg@50', 'ndcg@200']}

num_boost_round = 100
evallist = [(train_data, 'train'), (test_data, 'test')]

ltr_model = xgb.train(model_params, train_data, num_boost_round, evallist)
model_pred = ltr_model.predict(test_data)

pred_df = pd.DataFrame(model_pred)

pred_df.to_csv(
    "/Users/vladmatei/PycharmProjects/TextTechnologiesDS/Search_engine/search/retrieval_development/data/pred_lm6.txt",
    header=None,
    sep=" ",
    index=None)

plt.figure(figsize=(20, 20))
xgb.plot_importance(ltr_model, height=16)
plt.show()
