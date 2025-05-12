import os
import json
import csv
from utils import full_preprocess
from preprocess import normalize_text

# ============ Paths Setup ============

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INVESTOR_DATA_FILE = os.path.join(DATA_DIR, "investors.json")
INVESTOR_CACHE_FILE = os.path.join(DATA_DIR, "preprocessed_investors.json")
STARTUP_CACHE_FILE = os.path.join(DATA_DIR, "preprocessed_startups.json")
INTERACTIONS_FILE = os.path.join(DATA_DIR, "interactions.json")
INTERACTION_MATRIX_FILE = os.path.join(DATA_DIR, "interaction_matrix.csv")

investors = []
startups = []
interactions = {}        # {startup_id: [investor_ids]}
interaction_matrix = {}  # {investor_id: {startup_id: 1}}

# ============ Feature Extractors ============

def extract_investor_features(inv) -> dict:
    return {
        "industries": [normalize_text(i) for i in inv.get("Investment Industries", [])],
        "stages": [normalize_text(s) for s in inv.get("Investment Stages", [])],
        "location": normalize_text(inv.get("Location", "").split(",")[0].strip()),
        "teamSize": None,
        "foundedYear": None,
        "businessModel": ""
    }

def extract_startup_features(s) -> dict:
    return {
        "industries": [normalize_text(s.get("Industry", ""))],
        "stages": [normalize_text(s.get("Funding Stage", ""))],
        "location": normalize_text(s.get("Location", "").split(",")[0].strip()),
        "teamSize": s.get("Team Size", "").strip(),
        "foundedYear": s.get("Founded Year", ""),
        "businessModel": normalize_text(s.get("Business Model", "")),
        "revenueStage": normalize_text(s.get("Revenue Stage", "")),
        "customerSegment": normalize_text(s.get("Customer Segment", ""))
    }

# ============ Build Datasets ============

with open(INVESTOR_DATA_FILE, "r", encoding="utf-8") as f:
    raw_investors = json.load(f)

    for inv_id, inv in enumerate(raw_investors):
        inv_features = extract_investor_features(inv)
        processed_inv = full_preprocess(inv_features)
        inv["processed"] = processed_inv
        inv["id"] = inv_id
        investors.append(inv)

        for s_id, s in enumerate(inv.get("Invested Startups", [])):
            s_features = extract_startup_features(s)
            s_processed = full_preprocess(s_features)
            s["processed"] = s_processed
            s["investor_name"] = inv.get("Name", "Unknown")
            s["startup_id"] = f"{inv_id}_{s_id}"
            startups.append(s)

            # Update interaction map and matrix
            interactions.setdefault(s["startup_id"], []).append(inv_id)
            interaction_matrix.setdefault(inv_id, {})[s["startup_id"]] = 1

# ============ Write Outputs ============

with open(INVESTOR_CACHE_FILE, "w", encoding="utf-8") as f1:
    json.dump(investors, f1, indent=2)

with open(STARTUP_CACHE_FILE, "w", encoding="utf-8") as f2:
    json.dump(startups, f2, indent=2)

with open(INTERACTIONS_FILE, "w", encoding="utf-8") as f3:
    json.dump(interactions, f3, indent=2)

# ============ Write Interaction Matrix ============

startup_ids = sorted({s["startup_id"] for s in startups})

with open(INTERACTION_MATRIX_FILE, "w", newline='', encoding="utf-8") as f_csv:
    writer = csv.writer(f_csv)
    header = ["Investor_ID"] + startup_ids
    writer.writerow(header)

    for inv in investors:
        inv_id = inv["id"]
        row = [inv_id] + [interaction_matrix.get(inv_id, {}).get(sid, 0) for sid in startup_ids]
        writer.writerow(row)

print("✅ Preprocessing complete:")
print("   → preprocessed_investors.json")
print("   → preprocessed_startups.json")
print("   → interactions.json")
print("   → interaction_matrix.csv")
