import re
import unicodedata

# ===============================
# Canonical Mappings
# ===============================

INDUSTRY_ALIASES = {
    "fintech": "FinTech",
    "financial technology": "FinTech",
    "financial inclusion": "FinTech",
    "healthtech": "Healthcare",
    "health care": "Healthcare",
    "consumer internet": "Consumer",
    "retailtech": "RetailTech",
    "technology": "Tech",
    "tech": "Tech",
    "technology (sector agnostic)": "Tech",
    "ecommerce": "E-commerce",
    "edtech": "Education",
    "sector agnostic": "Various"
}

STAGE_ALIASES = {
    "pre seed": "Pre-Seed",
    "pre-seed": "Pre-Seed",
    "seed": "Seed",
    "series a": "Series A",
    "series b": "Series B",
    "series c": "Series C",
    "accelerator": "Accelerator",
    "growth": "Growth"
}

REGION_MAP = {
    "usa": "North America",
    "united states": "North America",
    "canada": "North America",
    "india": "Asia",
    "china": "Asia",
    "germany": "Europe",
    "france": "Europe",
    "uk": "Europe",
    "united kingdom": "Europe",
    "brazil": "South America",
    "australia": "Oceania"
    # Add more as needed
}

# ===============================
# Normalization Utilities
# ===============================

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.lower()
    text = re.sub(r"[\s\-_/]+", " ", text)  # normalize whitespace, dashes, underscores
    text = text.strip()
    return text

def canonicalize_industry(industry):
    key = normalize_text(industry)
    return INDUSTRY_ALIASES.get(key, industry.strip())

def canonicalize_stage(stage):
    key = normalize_text(stage)
    return STAGE_ALIASES.get(key, stage.strip())

def canonicalize_location(location):
    if not location:
        return "Unknown"
    key = normalize_text(location)
    for country_key, region in REGION_MAP.items():
        if country_key in key:
            return region
    return "Other"

# ===============================
# Numeric Bucketing
# ===============================

def bucket_team_size(size):
    try:
        size = int(size)
    except (ValueError, TypeError):
        return "Unknown"
    if size < 10:
        return "Small"
    elif size < 50:
        return "Medium"
    elif size < 200:
        return "Large"
    else:
        return "Enterprise"

def bucket_founded_year(year):
    try:
        year = int(year)
    except (ValueError, TypeError):
        return "Unknown"
    if year >= 2018:
        return "New"
    elif year >= 2010:
        return "Growing"
    else:
        return "Established"

# ===============================
# Unified Preprocessing Function
# ===============================

def preprocess_startup_payload(data):
    """
    Cleans and transforms incoming startup data into consistent format.
    Expected fields: industries, stages, location, teamSize, foundedYear
    """
    industries = [canonicalize_industry(i) for i in data.get("industries", [])]
    stages = [canonicalize_stage(s) for s in data.get("stages", [])]
    location = canonicalize_location(data.get("location", ""))
    team_bucket = bucket_team_size(data.get("teamSize", None))
    year_bucket = bucket_founded_year(data.get("foundedYear", None))
    business_model = normalize_text(data.get("businessModel", ""))

    return {
        "industries": industries,
        "stages": stages,
        "location_region": location,
        "team_bucket": team_bucket,
        "year_bucket": year_bucket,
        "business_model": business_model
    }
