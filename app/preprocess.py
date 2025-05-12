import re
import unicodedata

# ===============================
# Canonical Mappings
# ===============================

INDUSTRY_ALIASES = {
    "fintech": "FinTech",
    "financial technology": "FinTech",
    "financial inclusion": "FinTech",
    
    "ecommerce": "E-commerce",
    "e commerce": "E-commerce",
    "b2b ecommerce": "B2B E-commerce",
    "commerce": "Commerce",
    
    "consumer internet": "Consumer",
    "consumer tech": "Consumer",

    "developer tools": "Developer Tools",
    "devtools": "Developer Tools",

    "edtech": "Education",
    "education tech": "Education",
    
    "healthtech": "Healthcare",
    "health care": "Healthcare",

    "food tech": "Foodtech",
    "foodtech": "Foodtech",

    "ict": "ICT",
    "information and communication technology": "ICT",

    "it services": "IT Services",
    "software services": "IT Services",

    "impact tech": "Impact",
    "social impact": "Impact",

    "iot agritech": "IoT/AgriTech",
    "agritech": "AgriTech",
    
    "legal tech": "LegalTech",
    "legaltech": "LegalTech",
    
    "logistics tech": "Logistics",
    "supply chain": "Logistics",

    "martech": "MarTech",
    "marketing tech": "MarTech",

    "media tech": "Media",
    "publishing": "Media",

    "mobility tech": "Mobility",
    "ridesharing": "Mobility",

    "on demand": "On-demand",

    "platform": "Platforms",
    "platforms": "Platforms",

    "real estate tech": "PropTech",
    "proptech": "PropTech",

    "retail tech": "RetailTech",
    "retailtech": "RetailTech",

    "saas": "SaaS",
    "cloud software": "SaaS",

    "software": "Software",

    "technology": "Tech",
    "tech": "Tech",
    "technology (sector agnostic)": "Tech",
    
    "travel tech": "Traveltech",
    "traveltech": "Traveltech",

    "social tech": "Social Tech",

    "sector agnostic": "Various",
    "various": "Various"
}

STAGE_ALIASES = {
    "accelerator": "Accelerator",
    "acquired": "Acquired",
    "growth": "Growth",
    
    "pre seed": "Pre-Seed",
    "pre-seed": "Pre-Seed",

    "pre series a": "Pre-Series A",
    "pre-series a": "Pre-Series A",

    "seed": "Seed",

    "series a": "Series A",
    "series b": "Series B",
    "series b defunct": "Series B (Defunct)",
    "series c": "Series C",
    "series e": "Series E"
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
    if not size:
        return "Unknown"

    # Normalize string
    size_str = str(size).lower().strip().replace(",", "")
    
    # Handle ranges like "10-50"
    if "-" in size_str:
        try:
            parts = re.findall(r'\d+', size_str)
            avg = (int(parts[0]) + int(parts[1])) // 2
        except:
            return "Unknown"
    # Handle "100+", ">100", "over 50"
    elif "+" in size_str or ">" in size_str or "above" in size_str:
        try:
            number = int(re.findall(r'\d+', size_str)[0])
            avg = number + 10
        except:
            return "Unknown"
    # Handle "less than 10", "under 10"
    elif "less" in size_str or "under" in size_str:
        avg = 5
    else:
        try:
            avg = int(re.findall(r'\d+', size_str)[0])
        except:
            return "Unknown"

    if avg < 10:
        return "Small"
    elif avg < 50:
        return "Medium"
    elif avg < 200:
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
    Expected fields: industries, stages, location, teamSize, foundedYear, businessModel, revenueStage, customerSegment
    """
    industries = [canonicalize_industry(i) for i in data.get("industries", [])]
    stages = [canonicalize_stage(s) for s in data.get("stages", [])]
    location = normalize_text(data.get("location", ""))
    team_bucket = data.get("teamSize")
    year_bucket = data.get("foundedYear")
    business_model = normalize_text(data.get("businessModel", ""))
    revenue_stage = normalize_text(data.get("revenueStage", ""))
    customer_segment = normalize_text(data.get("customerSegment", ""))

    return {
        "industries": industries,
        "stages": stages,
        "location_region": location,
        "team_bucket": team_bucket,
        "year_bucket": year_bucket,
        "business_model": business_model,
        "revenue_stage": revenue_stage,
        "customer_segment": customer_segment
    }
