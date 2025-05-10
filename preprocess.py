# Preprocessing for Startup-Investor Recommender System
import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

# Load JSON file
with open("investors.json", "r", encoding="utf-8") as f:
    investors_data = json.load(f)

# Flatten investors and their startups into tabular format
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

    # Append investor record
    investor_records.append({
        "Investor Name": investor_name,
        "Industries": industries,
        "Stages": stages,
        "Location": location,
        "Ticket Size": ticket_size,
        "Number of Investments": num_investments,
        "Recent Activity Year": recent_year
    })

    # Append startup interactions
    for startup in investor.get("Invested Startups", []):
        interaction_records.append({
            "Investor Name": investor_name,
            "Startup Name": startup.get("Startup Name"),
            "Industry": startup.get("Industry"),
            "Location": startup.get("Location"),
            "Funding Stage": startup.get("Funding Stage"),
            "Business Model": startup.get("Business Model", "Unknown"),
            "Customer Segment": startup.get("Customer Segment", "Unknown"),
            "Revenue Stage": startup.get("Revenue Stage", "Unknown"),
            "Team Size": startup.get("Team Size", "Unknown"),
            "Founded Year": startup.get("Founded Year", "Unknown")
        })

# Convert to DataFrames
investors_df = pd.DataFrame(investor_records)
interactions_df = pd.DataFrame(interaction_records)

# Encode categorical features using MultiLabelBinarizer and get_dummies
mlb_industries = MultiLabelBinarizer()
industries_encoded = pd.DataFrame(mlb_industries.fit_transform(investors_df["Industries"]),
                                  columns=["Industry_" + i for i in mlb_industries.classes_])
investors_df = investors_df.drop("Industries", axis=1).join(industries_encoded)

mlb_stages = MultiLabelBinarizer()
stages_encoded = pd.DataFrame(mlb_stages.fit_transform(investors_df["Stages"]),
                              columns=["Stage_" + i.replace(" ", "_") for i in mlb_stages.classes_])
investors_df = investors_df.drop("Stages", axis=1).join(stages_encoded)

# Encode interaction-level startup features
interactions_df = pd.get_dummies(interactions_df, columns=["Business Model", "Customer Segment", "Revenue Stage"], prefix_sep="_")

# Map funding stage to numeric
funding_stage_map = {
    "Pre-Seed": 1,
    "Seed": 2,
    "Series A": 3,
    "Series B": 4,
    "Series C": 5,
    "Series D": 6,
    "Series E": 7,
    "Growth": 8
}
interactions_df["Funding Stage Numeric"] = interactions_df["Funding Stage"].map(funding_stage_map).fillna(0)

# Create interaction matrix (binary: 1 if investor invested in startup)
interaction_matrix = pd.pivot_table(
    interactions_df,
    values="Funding Stage Numeric",
    index="Startup Name",
    columns="Investor Name",
    aggfunc=lambda x: 1,
    fill_value=0
)
interaction_matrix.to_csv("interaction_matrix.csv")

# Save the processed DataFrames
investors_df.to_csv("./data/investors_encoded.csv", index=False)
interactions_df.to_csv("./data/interactions_encoded.csv", index=False)

print("✅ Preprocessing, encoding, and interaction matrix complete. Files saved as CSV.")
