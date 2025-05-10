import pandas as pd
import numpy as np

def load_data():
    investor_df = pd.read_csv("data/investors_encoded.csv")
    interaction_matrix = pd.read_csv("data/interaction_matrix.csv", index_col=0)

    # Extract only encoded columns
    encoded_cols = [c for c in investor_df.columns if c.startswith("Industry_") or c.startswith("Stage_")]
    features = investor_df[encoded_cols]

    return investor_df, features, interaction_matrix

def encode_input(startup_input, feature_cols):
    tokens = startup_input.get("industries", []) + startup_input.get("stages", [])
    vector = []
    for col in feature_cols:
        match = any(token.lower() in col.lower() for token in tokens)
        vector.append(1 if match else 0)
    return vector
