
# Enhanced Preprocessing for Startup-Investor Recommender System
import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from collections import defaultdict
import numpy as np

# Load JSON
with open("./data/investors.json", "r", encoding="utf-8") as f:
    investors_data = json.load(f)

# -------------------------------
# Step 1: Flatten Investor & Startup Data
# -------------------------------
investor_records = []
interaction_records = []
investor_aggregates = defaultdict(lambda: {
    "Team Sizes": [], "Founded Years": [],
    "Business Models": [], "Customer Segments": [],
    "Revenue Stages": [], "Industries": []
})

for investor in investors_data:
    name = investor["Name"]
    industries = investor.get("Investment Industries", [])
    stages = investor.get("Investment Stages", [])
    location = investor.get("Location", "")
    ticket_size = investor.get("Preferred Ticket Size", "Unknown")
    num_investments = investor.get("Number of Investments", 0)
    recent_year = investor.get("Recent Activity Year", "")
    role = investor.get("Investment Role", "")
    success = investor.get("Success Rate", "0%")
    past_types = investor.get("Past Investment Types", [])

    # Aggregate from invested startups
    for s in investor.get("Invested Startups", []):
        team_size = s.get("Team Size", "Unknown")
        try:
            numeric_team = int(team_size.replace("+", "").split("-")[-1])
        except:
            numeric_team = np.nan
        investor_aggregates[name]["Team Sizes"].append(numeric_team)

        try:
            year = int(s.get("Founded Year", 0))
            investor_aggregates[name]["Founded Years"].append(year)
        except:
            investor_aggregates[name]["Founded Years"].append(np.nan)

        investor_aggregates[name]["Business Models"].append(s.get("Business Model", "Unknown"))
        investor_aggregates[name]["Customer Segments"].append(s.get("Customer Segment", "Unknown"))
        investor_aggregates[name]["Revenue Stages"].append(s.get("Revenue Stage", "Unknown"))
        investor_aggregates[name]["Industries"].append(s.get("Industry", "Unknown"))

        interaction_records.append({
            "Investor Name": name,
            "Startup Name": s.get("Startup Name", "").strip().lower(),
            "Industry": s.get("Industry", "Unknown"),
            "Location": s.get("Location", "Unknown"),
            "Funding Stage": s.get("Funding Stage", "Unknown"),
            "Business Model": s.get("Business Model", "Unknown"),
            "Customer Segment": s.get("Customer Segment", "Unknown"),
            "Revenue Stage": s.get("Revenue Stage", "Unknown"),
            "Team Size": team_size,
            "Founded Year": s.get("Founded Year", "Unknown")
        })

    # Compute averages
    avg_team = np.nanmean(investor_aggregates[name]["Team Sizes"])
    if np.isnan(avg_team):
        avg_team = 10  # or median, etc.

    avg_age = np.nanmean([2025 - y for y in investor_aggregates[name]["Founded Years"] if not pd.isna(y)])

    investor_records.append({
        "Investor Name": name,
        "Industries": industries,
        "Stages": stages,
        "Location": location,
        "Ticket Size": ticket_size,
        "Number of Investments": num_investments,
        "Recent Activity Year": recent_year,
        "Investment Role": role,
        "Success Rate": success,
        "Avg Team Size": avg_team,
        "Avg Startup Age": avg_age,
        "Business Models": investor_aggregates[name]["Business Models"],
        "Customer Segments": investor_aggregates[name]["Customer Segments"],
        "Revenue Stages": investor_aggregates[name]["Revenue Stages"]
    })

# -------------------------------
# Step 2: Encode Investor Data
# -------------------------------
investors_df = pd.DataFrame(investor_records)

mlb_industries = MultiLabelBinarizer()
mlb_stages = MultiLabelBinarizer()
mlb_models = MultiLabelBinarizer()
mlb_segments = MultiLabelBinarizer()
mlb_revenue = MultiLabelBinarizer()

industries_encoded = pd.DataFrame(mlb_industries.fit_transform(investors_df["Industries"]), columns=["Ind_" + i for i in mlb_industries.classes_])
stages_encoded = pd.DataFrame(mlb_stages.fit_transform(investors_df["Stages"]), columns=["Stage_" + i.replace(" ", "_") for i in mlb_stages.classes_])
models_encoded = pd.DataFrame(mlb_models.fit_transform(investors_df["Business Models"]), columns=["BM_" + i for i in mlb_models.classes_])
segments_encoded = pd.DataFrame(mlb_segments.fit_transform(investors_df["Customer Segments"]), columns=["CS_" + i for i in mlb_segments.classes_])
revenue_encoded = pd.DataFrame(mlb_revenue.fit_transform(investors_df["Revenue Stages"]), columns=["Rev_" + i for i in mlb_revenue.classes_])

scaler = MinMaxScaler()
numerics_scaled = pd.DataFrame(scaler.fit_transform(investors_df[["Avg Team Size", "Avg Startup Age", "Number of Investments", "Recent Activity Year"]]), columns=["Norm_TeamSize", "Norm_Age", "Norm_Investments", "Norm_Activity"])

investors_final = pd.concat([
    investors_df[["Investor Name", "Location", "Ticket Size", "Recent Activity Year", "Number of Investments"]],
    industries_encoded,
    stages_encoded,
    models_encoded,
    segments_encoded,
    revenue_encoded,
    numerics_scaled
], axis=1)

# -------------------------------
# Step 3: Encode Interactions for Collaborative/Similarity
# -------------------------------
interactions_df = pd.DataFrame(interaction_records)
interactions_df["Startup Name"] = interactions_df["Startup Name"].str.strip().str.lower()
interactions_df = pd.get_dummies(interactions_df, columns=["Business Model", "Customer Segment", "Revenue Stage"], prefix_sep="_")

funding_stage_map = {
    "Pre-Seed": 1, "Seed": 2, "Series A": 3, "Series B": 4,
    "Series C": 5, "Series D": 6, "Series E": 7, "Growth": 8
}
interactions_df["Funding Stage Numeric"] = interactions_df["Funding Stage"].map(funding_stage_map).fillna(0)

interaction_matrix = pd.pivot_table(
    interactions_df,
    values="Funding Stage Numeric",
    index="Startup Name",
    columns="Investor Name",
    aggfunc=lambda x: 1,
    fill_value=0
)

# -------------------------------
# Step 4: Save Outputs
# -------------------------------
interaction_matrix.to_csv("./data/interaction_matrix.csv")
investors_final.to_csv("./data/investors_encoded.csv", index=False)
interactions_df.to_csv("./data/interactions_encoded.csv", index=False)

# Startup Features
startup_df = interactions_df.drop_duplicates(subset=["Startup Name"]).reset_index(drop=True)
startup_df_meta = startup_df[["Startup Name", "Industry", "Funding Stage", "Funding Stage Numeric"]]
startup_df_meta.loc[:, "Funding Stage Numeric"] = (startup_df_meta["Funding Stage Numeric"] - startup_df_meta["Funding Stage Numeric"].min()) / max(1, startup_df_meta["Funding Stage Numeric"].max())

startup_feature_columns = startup_df.filter(regex="^(Business Model_|Customer Segment_|Revenue Stage_)")
startup_industry_encoded = pd.get_dummies(startup_df["Industry"], prefix="Industry")

startup_features = pd.concat([
    startup_df_meta[["Funding Stage Numeric"]],
    startup_industry_encoded,
    startup_feature_columns
], axis=1)

startup_df_meta.to_csv("./data/startups_profiles.csv", index=False)
startup_features.to_csv("./data/startups_features.csv", index=False)

print("✅ Enhanced investor and startup data saved.")
