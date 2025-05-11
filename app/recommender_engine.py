import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils import full_preprocess
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INVESTOR_CACHE_FILE = os.path.join(DATA_DIR, "preprocessed_investors.json")
STARTUP_CACHE_FILE = os.path.join(DATA_DIR, "preprocessed_startups.json")
INTERACTIONS_FILE = os.path.join(DATA_DIR, "interactions.json")

INVESTORS = []
STARTUPS = []
INTERACTIONS = {}

def load_data():
    global INVESTORS, STARTUPS, INTERACTIONS
    with open(INVESTOR_CACHE_FILE, "r") as f1:
        INVESTORS = json.load(f1)
    with open(STARTUP_CACHE_FILE, "r") as f2:
        STARTUPS = json.load(f2)
    with open(INTERACTIONS_FILE, "r") as f3:
        INTERACTIONS = json.load(f3)

load_data()

def compute_similarity(vec1, vec2):
    if not vec1 or not vec2 or not any(vec1) or not any(vec2):
        return 0.0
    try:
        return float(cosine_similarity([vec1], [vec2])[0][0])
    except Exception as e:
        logging.warning(f"Similarity error: {e}")
        return 0.0

def format_investor_result(score, inv):
    return {
        "id": inv.get("id"),
        "Investor Name": inv.get("Name", "N/A"),
        "Location": inv.get("Location", "N/A"),
        "Score": round(score, 3),
        "Investor Bio": inv.get("Investor Bio", "—"),
        "Past Investment Types": inv.get("Past Investment Types", "—"),
        "Investment Stages": inv.get("Investment Stages", "—")
    }

def calculate_similarity_score(encoded_input, encoded_target):
    weights = {
        "industry_vec": 0.4,
        "stage_vec": 0.2,
        "location_vec": 0.15,
        "team_vec": 0.15,
        "year_vec": 0.1
    }

    score = 0.0
    for key, weight in weights.items():
        sim = compute_similarity(encoded_input.get(key, []), encoded_target.get(key, []))
        score += weight * sim
    return score

def recommend_by_content(encoded_input, top_k=10):
    scores = []
    for inv in INVESTORS:
        inv_vecs = inv["processed"]["encoded"]
        score = calculate_similarity_score(encoded_input, inv_vecs)
        if score > 0.1:
            scores.append((score, inv))
    sorted_results = sorted(scores, key=lambda x: x[0], reverse=True)
    return [format_investor_result(score, inv) for score, inv in sorted_results[:top_k]]

def recommend_by_collaborative(encoded_input, top_k=10):
    score_map = {}
    for startup in STARTUPS:
        s_vecs = startup["processed"]["encoded"]
        sim = calculate_similarity_score(encoded_input, s_vecs)
        if sim > 0.1:
            startup_id = startup.get("startup_id")
            for inv_id in INTERACTIONS.get(startup_id, []):
                score_map[inv_id] = score_map.get(inv_id, 0) + sim
    sorted_results = sorted([(score, INVESTORS[inv_id]) for inv_id, score in score_map.items()], key=lambda x: x[0], reverse=True)
    return [format_investor_result(score, inv) for score, inv in sorted_results[:top_k]]

def recommend_by_hybrid(encoded_input, activity_weight=0.5, investment_weight=0.5, top_k=10):
    content_scores = recommend_by_content(encoded_input, top_k=top_k * 2)
    collaborative_scores = recommend_by_collaborative(encoded_input, top_k=top_k * 2)

    content_dict = {c["id"]: c for c in content_scores}
    hybrid_results = []

    for collab in collaborative_scores:
        inv_id = collab["id"]
        content_score = content_dict.get(inv_id, {}).get("Score", 0)
        hybrid_score = activity_weight * content_score + investment_weight * collab["Score"]
        collab["Score"] = round(hybrid_score, 3)
        hybrid_results.append(collab)

    return sorted(hybrid_results, key=lambda x: x["Score"], reverse=True)[:top_k]

def recommend_similar_startups(input_data, top_k=10):
    encoded_input = input_data["encoded"]
    scores = []
    for s in STARTUPS:
        s_vecs = s["processed"]["encoded"]
        score = calculate_similarity_score(encoded_input, s_vecs)
        scores.append((score, s))
    sorted_results = sorted(scores, key=lambda x: x[0], reverse=True)
    return [
        {
            "Startup Name": s.get("Startup Name", "N/A"),
            "Industry": s.get("Industry", "—"),
            "Location": s.get("Location", "—"),
            "Funding Stage": s.get("Funding Stage", "—"),
            "Score": round(score, 3),
            "Investor": s.get("investor_name", "—")
        }
        for score, s in sorted_results[:top_k]
    ]

def get_recommendations(data: dict, top_k: int = 6):
    rs_type = data.get("rs_type", "content")
    encoded_input = data["processed"]["encoded"]

    if rs_type == "content":
        return recommend_by_content(encoded_input, top_k)
    elif rs_type == "collaborative":
        return recommend_by_collaborative(encoded_input, top_k)
    elif rs_type == "hybrid":
        return recommend_by_hybrid(
            encoded_input,
            data.get("activityWeight", 0.5),
            data.get("investmentWeight", 0.5),
            top_k
        )
    elif rs_type == "startup_similarity":
        return recommend_similar_startups(data["processed"], top_k)
    return []
