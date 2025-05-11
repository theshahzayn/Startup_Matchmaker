import os
import json
from typing import List, Dict
from preprocess import (
    normalize_text,
    canonicalize_industry,
    canonicalize_stage,
    bucket_team_size,
    bucket_founded_year,
    canonicalize_location
)

# ===============================
# Load Dynamic Label Constants
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LABELS_PATH = os.path.join(BASE_DIR, "data", "labels.json")

with open(LABELS_PATH, "r") as f:
    label_data = json.load(f)

INDUSTRY_LABELS = sorted(list(set([canonicalize_industry(i) for i in label_data.get("industries", []) if i])))
STAGE_LABELS = sorted(list(set([canonicalize_stage(s) for s in label_data.get("stages", []) if s])))
LOCATION_LABELS = sorted([normalize_text(l) for l in label_data.get("locations", []) if l])

TEAM_BUCKETS = ["Small", "Medium", "Large", "Enterprise", "Unknown"]
YEAR_BUCKETS = ["New", "Growing", "Established", "Unknown"]

# ===============================
# Encoder / Decoder Utilities
# ===============================

def encode_label(value: str, label_list: List[str]) -> int:
    try:
        return label_list.index(value)
    except ValueError:
        return -1

def decode_label(index: int, label_list: List[str]) -> str:
    return label_list[index] if 0 <= index < len(label_list) else "Unknown"

def one_hot_encode(value: str, label_list: List[str]) -> List[int]:
    vec = [0] * len(label_list)
    idx = encode_label(value, label_list)
    if idx != -1:
        vec[idx] = 1
    return vec

def multi_hot_encode(values: List[str], label_list: List[str]) -> List[int]:
    vec = [0] * len(label_list)
    for val in values:
        idx = encode_label(val, label_list)
        if idx != -1:
            vec[idx] = 1
    return vec

# ===============================
# Common Pipeline Helpers
# ===============================

def full_preprocess(data: Dict) -> Dict:
    cleaned = {
        "industries": [canonicalize_industry(i) for i in data.get("industries", [])],
        "stages": [canonicalize_stage(s) for s in data.get("stages", [])],
        "location_region": data.get("location", "").split(",")[0].strip(),
        "team_bucket": bucket_team_size(data.get("teamSize", None)),
        "year_bucket": bucket_founded_year(data.get("foundedYear", None)),
        "business_model": normalize_text(data.get("businessModel", "")),
        "revenue_stage": normalize_text(data.get("revenueStage", "")),
        "customer_segment": normalize_text(data.get("customerSegment", ""))
    }

    encoded = {
        "industry_vec": multi_hot_encode(cleaned["industries"], INDUSTRY_LABELS),
        "stage_vec": multi_hot_encode(cleaned["stages"], STAGE_LABELS),
        "location_vec": one_hot_encode(cleaned["location_region"], LOCATION_LABELS),
        "team_vec": one_hot_encode(cleaned["team_bucket"], TEAM_BUCKETS),
        "year_vec": one_hot_encode(cleaned["year_bucket"], YEAR_BUCKETS),
    }

    return {
        "raw": cleaned,
        "encoded": encoded
    }
