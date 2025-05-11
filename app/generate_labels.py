import os
import json
from preprocess import (
    normalize_text,
    canonicalize_industry,
    canonicalize_stage
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INVESTOR_FILE = os.path.join(DATA_DIR, "investors.json")
LABELS_FILE = os.path.join(DATA_DIR, "labels.json")

# Label buckets
industries = set()
stages = set()
locations = set()
team_sizes = set()
founded_years = set()
business_models = set()
revenue_stages = set()
customer_segments = set()

def extract_city(location: str) -> str:
    if not location:
        return ""
    city = location.split(",")[0].strip()
    return normalize_text(city).title()

with open(INVESTOR_FILE, "r") as f:
    data = json.load(f)

for inv in data:
    industries.update([canonicalize_industry(i) for i in inv.get("Investment Industries", [])])
    stages.update([canonicalize_stage(s) for s in inv.get("Investment Stages", [])])
    locations.add(extract_city(inv.get("Location", "")))

    for s in inv.get("Invested Startups", []):
        industries.add(canonicalize_industry(s.get("Industry", "")))
        stages.add(canonicalize_stage(s.get("Funding Stage", "")))
        locations.add(extract_city(s.get("Location", "")))

        if s.get("Team Size"):
            team_sizes.add((s["Team Size"]))
        if s.get("Founded Year"):
            founded_years.add(str(s["Founded Year"]).strip())
        if s.get("Business Model"):
            business_models.add(normalize_text(s["Business Model"]))
        if s.get("Revenue Stage"):
            revenue_stages.add(normalize_text(s["Revenue Stage"]))
        if s.get("Customer Segment"):
            customer_segments.add(normalize_text(s["Customer Segment"]))

# Clean and sort label sets
def clean(items):
    return sorted({i for i in items if i and i.lower() not in ["n/a", "unknown", ""]})

labels = {
    "industries": clean(industries),
    "stages": clean(stages),
    "locations": clean(locations),
    "team_sizes": clean(team_sizes),
    "founded_years": sorted(founded_years),
    "business_models": clean(business_models),
    "revenue_stages": clean(revenue_stages),
    "customer_segments": clean(customer_segments)
}

with open(LABELS_FILE, "w") as f:
    json.dump(labels, f, indent=2)

print("✅ Label extraction complete → labels.json")
