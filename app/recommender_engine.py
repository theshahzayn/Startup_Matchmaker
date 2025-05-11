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
    encoded = encode_input(input_data, investor_features.columns)

    # Rebuild query vector to match enhanced_features shape
    query_vec = encoded + [
        float(input_data.get("activityWeight", 0.5)),
        float(input_data.get("investmentWeight", 0.5))
    ]

    if len(query_vec) != enhanced_features.shape[1]:
        raise ValueError("Encoded input does not match feature matrix dimensions.")

    scores = cosine_similarity([query_vec], enhanced_features.values).flatten()

    # -----------------------------
    # Location bonus (optional column)
    user_location = input_data.get("location", "").strip().lower()
    if "Location" in investor_df.columns:
        location_bonus = np.array([
            0.05 if user_location and user_location in str(loc).strip().lower() else 0.0
            for loc in investor_df["Location"]
        ])
    else:
        location_bonus = np.zeros(len(investor_df))

    # -----------------------------
    # Team size similarity (if team data available)
    try:
        team_size = float(input_data.get("teamSize", 10))
        if "Avg Team Size" in investor_df.columns and "Norm_TeamSize" in investor_df.columns:
            team_scaled = (team_size - investor_df["Avg Team Size"].min()) / (
                investor_df["Avg Team Size"].max() - investor_df["Avg Team Size"].min() + 1e-8
            )
            team_similarity = 1 - abs(investor_df["Norm_TeamSize"] - team_scaled)
        else:
            team_similarity = np.zeros(len(investor_df))
    except:
        team_similarity = np.zeros(len(investor_df))

    # -----------------------------
    # Final scoring
    final_scores = scores * 0.85 + location_bonus + team_similarity * 0.1
    top_idxs = np.argsort(final_scores)[::-1][:top_k]

    results = []
    for i in top_idxs:
        r = investor_df.iloc[i]
        results.append({
            "Investor Name": str(r.get("Investor Name", "N/A")),
            "Location": str(r.get("Location", "N/A")),
            "Ticket Size": str(r.get("Ticket Size", "N/A")),
            "Recent Activity Year": int(r.get("Recent Activity Year", 0)),
            "Number of Investments": int(r.get("Number of Investments", 0)),
            "Score": float(round(final_scores[i], 3))
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
    try:
        content_scores = recommend_content(input_data, top_k=20)
    except Exception as e:
        print("Content-based failed:", e)
        content_scores = []

    try:
        collab_scores  = recommend_collaborative(input_data, top_k=20)
    except Exception as e:
        print("Collaborative failed:", e)
        collab_scores = []

    merged = {}
    for rec in content_scores:
        merged[rec["Investor Name"]] = merged.get(rec["Investor Name"], 0) + rec["Score"] * 0.6
    for rec in collab_scores:
        merged[rec["Investor Name"]] = merged.get(rec["Investor Name"], 0) + rec["Score"] * 0.4

    top_pairs = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:top_k]
    results = []
    for name, score in top_pairs:
        row = investor_df[investor_df["Investor Name"] == name]
        if not row.empty:
            r = row.iloc[0]
            results.append({
                "Investor Name": name,
                "Score": float(round(score, 3)),
                "Location": str(r.get("Location", "N/A")),
                "Ticket Size": str(r.get("Ticket Size", "N/A")),
                "Recent Activity Year": int(r.get("Recent Activity Year", 0)),
                "Number of Investments": int(r.get("Number of Investments", 0))
            })
    return results


# -----------------------------
# Startup Similarity Recommender (Fixed to return startups, not investors)
# -----------------------------
startup_profiles = pd.read_csv("./app/data/startups_profiles.csv")
startup_features = pd.read_csv("./app/data/startups_features.csv")

def recommend_similar_startups(input_data, top_k=6):
    industries = input_data.get("industries", [])
    stages     = input_data.get("stages", [])

    # Build query vector
    query_vector = []
    for col in startup_features.columns:
        if col.startswith("Industry_"):
            query_vector.append(1 if col.replace("Industry_", "") in industries else 0)
        elif col == "Funding Stage Numeric":
            # Use the average stage index of selected stages
            stage_map = {"Pre-Seed": 1, "Seed": 2, "Series A": 3, "Series B": 4, "Series C": 5, "Growth": 6}
            numeric_stage = np.mean([stage_map.get(stage, 0) for stage in stages]) if stages else 0
            query_vector.append(numeric_stage)
        else:
            query_vector.append(0)

    scores   = cosine_similarity([query_vector], startup_features.values).flatten()
    top_idxs = np.argsort(scores)[::-1][:top_k]

    recommendations = []
    for idx in top_idxs:
        row = startup_profiles.iloc[idx]
        recommendations.append({
            "Startup Name":     row["Startup Name"],
            "Industry":         row["Industry"],
            "Funding Stage":    row["Funding Stage Numeric"],
            "Similarity Score": round(scores[idx], 3)
        })

    return recommendations

