import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from utils import load_data, encode_input

# -----------------------------
# Load Data
# -----------------------------
investor_df, investor_features, interaction_matrix = load_data()
startup_df = pd.read_csv("./app/data/interactions_encoded.csv")

# -----------------------------
# Normalize Investor Data
# -----------------------------
investor_df["Recent Activity Year"]   = investor_df["Recent Activity Year"].fillna(2000)
investor_df["Number of Investments"]  = investor_df["Number of Investments"].fillna(0)
investor_df["Norm_Activity"]          = (
    investor_df["Recent Activity Year"] - investor_df["Recent Activity Year"].min()
) / (investor_df["Recent Activity Year"].max() - investor_df["Recent Activity Year"].min())
investor_df["Norm_Investments"]       = (
    investor_df["Number of Investments"] - investor_df["Number of Investments"].min()
) / (investor_df["Number of Investments"].max() - investor_df["Number of Investments"].min())

enhanced_features = investor_features.copy()
enhanced_features["Norm_Activity"]     = investor_df["Norm_Activity"]
enhanced_features["Norm_Investments"]  = investor_df["Norm_Investments"]

# -----------------------------
# Content-Based Recommender
# -----------------------------
def recommend_content(input_data, top_k=6):
    encoded   = encode_input(input_data, investor_features.columns)
    activity  = input_data.get("activityWeight", 0.5)
    investment= input_data.get("investmentWeight", 0.5)
    query_vec = encoded + [activity, investment]

    scores     = cosine_similarity([query_vec], enhanced_features.values).flatten()
    top_idxs   = np.argsort(scores)[::-1][:top_k]

    results = []
    for i in top_idxs:
        r = investor_df.iloc[i]
        results.append({
            "Investor Name":            str(r["Investor Name"]),
            "Location":                 str(r["Location"]),
            "Ticket Size":              str(r["Ticket Size"]),
            "Recent Activity Year":     int(r["Recent Activity Year"]),
            "Number of Investments":    int(r["Number of Investments"]),
            "Score":                    float(round(scores[i], 3))
        })
    return results

# -----------------------------
# Collaborative Recommender
# -----------------------------
def recommend_collaborative(input_data, top_k=6):
    ranked = interaction_matrix.sum(axis=0).sort_values(ascending=False)[:top_k]
    results = []
    for investor, score in ranked.items():
        row = investor_df[investor_df["Investor Name"] == investor]
        if not row.empty:
            r = row.iloc[0]
            results.append({
                "Investor Name":            str(investor),
                "Score":                    int(score),
                "Location":                 str(r["Location"]),
                "Ticket Size":              str(r["Ticket Size"]),
                "Recent Activity Year":     int(r["Recent Activity Year"]),
                "Number of Investments":    int(r["Number of Investments"])
            })
    return results

# -----------------------------
# Hybrid Recommender
# -----------------------------
def recommend_hybrid(input_data, top_k=6):
    content_scores = recommend_content(input_data, top_k=20)
    collab_scores  = recommend_collaborative(input_data, top_k=20)

    merged = {}
    for rec in content_scores:
        merged[rec["Investor Name"]] = merged.get(rec["Investor Name"], 0) + rec["Score"] * 0.6
    for rec in collab_scores:
        merged[rec["Investor Name"]] = merged.get(rec["Investor Name"], 0) + rec["Score"] * 0.4

    top_pairs = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:top_k]
    results   = []
    for name, score in top_pairs:
        row = investor_df[investor_df["Investor Name"] == name].iloc[0]
        results.append({
            "Investor Name":            name,
            "Score":                    float(round(score, 3)),
            "Location":                 str(row["Location"]),
            "Ticket Size":              str(row["Ticket Size"]),
            "Recent Activity Year":     int(row["Recent Activity Year"]),
            "Number of Investments":    int(row["Number of Investments"])
        })
    return results

# -----------------------------
# Startup Similarity Recommender
# -----------------------------
# Build one-hot feature matrix for startups
startup_ind = pd.get_dummies(startup_df["Industry"], prefix="Industry")
startup_stg = pd.get_dummies(startup_df["Funding Stage"], prefix="Stage")
startup_features = pd.concat([startup_ind, startup_stg], axis=1)

def recommend_similar_startups(input_data, top_k=6):
    # Build query vector from selected industries & stages
    industries = input_data.get("industries", [])
    stages     = input_data.get("stages", [])

    query = []
    for col in startup_features.columns:
        if col.startswith("Industry_"):
            query.append(1 if col.replace("Industry_", "") in industries else 0)
        elif col.startswith("Stage_"):
            query.append(1 if col.replace("Stage_", "") in stages else 0)
        else:
            query.append(0)

    # Compute similarity to all startups
    scores   = cosine_similarity([query], startup_features.values).flatten()
    top_idxs = np.argsort(scores)[::-1][:top_k]

    results = []
    for i in top_idxs:
        row = startup_df.iloc[i]
        results.append({
            "Startup Name":     row["Startup Name"],
            "Industry":         row["Industry"],
            "Funding Stage":    row["Funding Stage"],
            "Similarity Score": float(round(scores[i], 3))
        })
    return results
