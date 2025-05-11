from marshmallow import Schema, fields, ValidationError, post_load
from utils import full_preprocess

# ===============================
# Input Validation Schema
# ===============================

class RecommendRequestSchema(Schema):
    industries = fields.List(fields.String(), required=True)
    stages = fields.List(fields.String(), required=True)
    rs_type = fields.String(required=True)
    
    # Optional with defaults or nullable
    activityWeight = fields.Float(missing=0.5)
    investmentWeight = fields.Float(missing=0.5)
    
    teamSize = fields.String(allow_none=True)
    foundedYear = fields.String(allow_none=True)
    location = fields.String(allow_none=True)
    businessModel = fields.String(allow_none=True)
    revenueStage = fields.Str()
    customerSegment = fields.Str()

    @post_load
    def preprocess(self, data, **kwargs):
        """
        Runs full preprocessing after schema validation.
        Injects both raw cleaned data and encoded vectors.
        """
        processed = full_preprocess(data)
        data["processed"] = processed  # Includes both raw and encoded versions
        return data

# ===============================
# Utility for Validation
# ===============================

def validate_recommend_request(json_data):
    """
    Validate input JSON using RecommendRequestSchema.
    Returns: (cleaned_data, errors)
    """
    schema = RecommendRequestSchema()
    try:
        data = schema.load(json_data)
        return data, None
    except ValidationError as err:
        return None, err.messages
