import pandas as pd
import xgboost as xgb
from datetime import datetime



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
    df_DMatrix = xgb.DMatrix(X, label=y) # Create the DMatrix which is pretty much a dataframe but optimised
    grp = grp.map(pd.to_numeric)
    df_DMatrix.set_group(grp_info_counts)
    print("Number of rows y label = " + str(len(grp)))
    print("Shape of X = " + str(len(X.shape)))
    return df_DMatrix


# Reading the path as 'data/train.pkl' did not work (not found) but the absolute path seems to work

print("Started Loading data ", datetime.now().strftime("%H:%M:%S"))
train_df = pd.read_pickle(
    "/Users/vladmatei/PycharmProjects/TextTechnologiesDS/Search_engine/search/retrieval_development/data/train.pkl")
test_df = pd.read_pickle(
    "/Users/vladmatei/PycharmProjects/TextTechnologiesDS/Search_engine/search/retrieval_development/data/test.pkl")
print("Finished Loading data ", datetime.now().strftime("%H:%M:%S"))


print("Started Creating train D_matrix ", datetime.now().strftime("%H:%M:%S"))
train_data = get_D_matrix(train_df)
print("Finished it", datetime.now().strftime("%H:%M:%S"))

print("Started Creating test D_matrix ", datetime.now().strftime("%H:%M:%S"))
test_data = get_D_matrix(test_df)
print("Finished it", datetime.now().strftime("%H:%M:%S"))