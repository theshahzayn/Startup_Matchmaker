
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils import load_data, encode_input

# Load data once
investor_df, investor_features, interaction_matrix = load_data()

# Normalize additional features
investor_df["Recent Activity Year"] = investor_df["Recent Activity Year"].fillna(2000)
investor_df["Number of Investments"] = investor_df["Number of Investments"].fillna(0)
investor_df["Norm_Activity"] = (investor_df["Recent Activity Year"] - investor_df["Recent Activity Year"].min()) / \
                               (investor_df["Recent Activity Year"].max() - investor_df["Recent Activity Year"].min())
investor_df["Norm_Investments"] = (investor_df["Number of Investments"] - investor_df["Number of Investments"].min()) / \
                                   (investor_df["Number of Investments"].max() - investor_df["Number of Investments"].min())

# Add these features to the content matrix
enhanced_features = investor_features.copy()
enhanced_features["Norm_Activity"] = investor_df["Norm_Activity"]
enhanced_features["Norm_Investments"] = investor_df["Norm_Investments"]

def recommend_content(input_data, top_k=5):
    encoded = encode_input(input_data, investor_features.columns)
    extended_vector = encoded + [0.5, 0.5]
    scores = cosine_similarity([extended_vector], enhanced_features.values).flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]

    records = []
    for i in top_indices:
        r = investor_df.iloc[i]
        records.append({
            "Investor Name": str(r["Investor Name"]),
            "Location": str(r["Location"]),
            "Ticket Size": str(r["Ticket Size"]),
            "Recent Activity Year": int(r["Recent Activity Year"]),
            "Number of Investments": int(r["Number of Investments"]),
            "Score": float(round(scores[i], 3))
        })
    return records

def recommend_collaborative(input_data, top_k=5):
    ranked = interaction_matrix.sum(axis=0).sort_values(ascending=False)[:top_k]
    recommendations = []
    for investor_name, score in ranked.items():
        row = investor_df[investor_df["Investor Name"] == investor_name]
        if not row.empty:
            r = row.iloc[0]
            recommendations.append({
                "Investor Name": str(investor_name),
                "Score": int(score),
                "Location": str(r["Location"]),
                "Ticket Size": str(r["Ticket Size"]),
                "Recent Activity Year": int(r["Recent Activity Year"]),
                "Number of Investments": int(r["Number of Investments"])
            })
    return recommendations

def recommend_hybrid(input_data, top_k=5):
    content_scores = recommend_content(input_data, top_k=20)
    collab_scores = recommend_collaborative(input_data, top_k=20)

    merged = {}
    for rec in content_scores:
        name = rec["Investor Name"]
        merged[name] = merged.get(name, 0) + rec["Score"] * 0.6

    for rec in collab_scores:
        name = rec["Investor Name"]
        merged[name] = merged.get(name, 0) + rec["Score"] * 0.4

    sorted_merge = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:top_k]

    final = []
    for name, score in sorted_merge:
        row = investor_df[investor_df["Investor Name"] == name]
        if not row.empty:
            r = row.iloc[0]
            final.append({
                "Investor Name": str(name),
                "Score": float(round(score, 3)),
                "Location": str(r["Location"]),
                "Ticket Size": str(r["Ticket Size"]),
                "Recent Activity Year": int(r["Recent Activity Year"]),
                "Number of Investments": int(r["Number of Investments"])
            })

    return final
