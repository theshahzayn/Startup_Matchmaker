# Enhanced Preprocessing for Startup-Investor Recommender System
import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

# Load JSON
with open("./data/investors.json", "r", encoding="utf-8") as f:
    investors_data = json.load(f)

# -------------------------------
# Step 1: Flatten Investor & Startup Data
# -------------------------------
investor_records = []
interaction_records = []

for investor in investors_data:
    investor_name = investor["Name"]
    industries = investor.get("Investment Industries", [])
    stages = investor.get("Investment Stages", [])
    location = investor.get("Location", "")
    ticket_size = investor.get("Preferred Ticket Size", "Unknown")
    num_investments = investor.get("Number of Investments", 0)
    recent_year = investor.get("Recent Activity Year", "")

    investor_records.append({
        "Investor Name": investor_name,
        "Industries": industries,
        "Stages": stages,
        "Location": location,
        "Ticket Size": ticket_size,
        "Number of Investments": num_investments,
        "Recent Activity Year": recent_year
    })

    for startup in investor.get("Invested Startups", []):
        interaction_records.append({
            "Investor Name": investor_name,
            "Startup Name": startup.get("Startup Name", "").strip(),
            "Industry": startup.get("Industry", "Unknown"),
            "Location": startup.get("Location", "Unknown"),
            "Funding Stage": startup.get("Funding Stage", "Unknown"),
            "Business Model": startup.get("Business Model", "Unknown"),
            "Customer Segment": startup.get("Customer Segment", "Unknown"),
            "Revenue Stage": startup.get("Revenue Stage", "Unknown"),
            "Team Size": startup.get("Team Size", "Unknown"),
            "Founded Year": startup.get("Founded Year", "Unknown")
        })

# -------------------------------
# Step 2: Investor Encoding
# -------------------------------
investors_df = pd.DataFrame(investor_records)

mlb_industries = MultiLabelBinarizer()
industries_encoded = pd.DataFrame(
    mlb_industries.fit_transform(investors_df["Industries"]),
    columns=["Industry_" + i for i in mlb_industries.classes_]
)

mlb_stages = MultiLabelBinarizer()
stages_encoded = pd.DataFrame(
    mlb_stages.fit_transform(investors_df["Stages"]),
    columns=["Stage_" + i.replace(" ", "_") for i in mlb_stages.classes_]
)

investors_df = investors_df.drop(["Industries", "Stages"], axis=1)
investors_df = investors_df.join(industries_encoded).join(stages_encoded)

# -------------------------------
# Step 3: Startup Interaction Encoding
# -------------------------------
interactions_df = pd.DataFrame(interaction_records)
interactions_df["Startup Name"] = interactions_df["Startup Name"].str.strip().str.lower()

# Encode categorical startup features
interactions_df = pd.get_dummies(
    interactions_df,
    columns=["Business Model", "Customer Segment", "Revenue Stage"],
    prefix_sep="_"
)

# Funding Stage mapping
funding_stage_map = {
    "Pre-Seed": 1, "Seed": 2, "Series A": 3, "Series B": 4,
    "Series C": 5, "Series D": 6, "Series E": 7, "Growth": 8
}
interactions_df["Funding Stage Numeric"] = (
    interactions_df["Funding Stage"].map(funding_stage_map).fillna(0)
)

# -------------------------------
# Step 4: Save Investor & Interaction Data
# -------------------------------
interaction_matrix = pd.pivot_table(
    interactions_df,
    values="Funding Stage Numeric",
    index="Startup Name",
    columns="Investor Name",
    aggfunc=lambda x: 1,
    fill_value=0
)
interaction_matrix.to_csv("./data/interaction_matrix.csv")
investors_df.to_csv("./data/investors_encoded.csv", index=False)
interactions_df.to_csv("./data/interactions_encoded.csv", index=False)

print("✅ Investor & interaction data processed.")

# -------------------------------
# Step 5: Startup Profile Generation
# -------------------------------
startup_df = (
    interactions_df
    .drop_duplicates(subset=["Startup Name"])
    .reset_index(drop=True)
)

startup_df_meta = startup_df[[
    "Startup Name", "Industry", "Funding Stage", "Funding Stage Numeric"
]]

# Normalize numeric field
startup_df_meta.loc[:, "Funding Stage Numeric"] = (
    startup_df_meta["Funding Stage Numeric"] - startup_df_meta["Funding Stage Numeric"].min()
) / max(1, startup_df_meta["Funding Stage Numeric"].max() - startup_df_meta["Funding Stage Numeric"].min())


# Extract encoded features
startup_feature_columns = startup_df.filter(regex="^(Business Model_|Customer Segment_|Revenue Stage_)")
startup_industry_encoded = pd.get_dummies(startup_df["Industry"], prefix="Industry")

startup_features = pd.concat([
    startup_df_meta[["Funding Stage Numeric"]],
    startup_industry_encoded,
    startup_feature_columns
], axis=1)

startup_df_meta.to_csv("./data/startups_profiles.csv", index=False)
startup_features.to_csv("./data/startups_features.csv", index=False)

print("✅ Startup profiles and feature matrix saved.")
