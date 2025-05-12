from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from schemas import validate_recommend_request
from recommender_engine import get_recommendations, INVESTORS
import os
import json


app = Flask(__name__)
CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

api = Blueprint('api', __name__)

@api.route("/recommend", methods=["POST"])
def recommend_route():
    json_data = request.get_json()
    print("\n🔵 Received POST /recommend with data:")
    print(json_data)

    if not json_data:
        print("❌ No JSON received.")
        return jsonify({"error": "Empty request"}), 400

    validated_data, errors = validate_recommend_request(json_data)
    if errors:
        print("❌ Validation errors:")
        print(errors)
        return jsonify({"error": "Invalid payload", "details": errors}), 400

    print("✅ Validated & Preprocessed Input:")
    print(validated_data.get("processed", {}))

    try:
        results = get_recommendations(validated_data)
        print(f"✅ Generated {len(results)} recommendations.")
        return jsonify({"recommendations": results}), 200
    
    except Exception as e:
        print("🔥 ERROR during recommendation:")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@api.route("/investor/<string:name>", methods=["GET"])
def investor_detail(name):
    name_lower = name.lower()

    for investor in enumerate(INVESTORS):
        # if investor is a tuple, unpack it
        if isinstance(investor, tuple):
            _, investor = investor

        if investor.get("name", "").lower() == name_lower:
            print(f"✅ Found investor '{name}")

            return jsonify({
                "name": investor.get("name"),
                "location": investor.get("location"),
                "industries": investor.get("industries"),
                "ticket_size": investor.get("ticket_size"),
                "num_investments": investor.get("num_investments"),
                "recent_year": investor.get("recent_year"),
                "raw": investor.get("processed", {}).get("raw", {})
            })
        
        return jsonify({"error": "Investor not found"}), 404

@api.route("/startup/<string:name>", methods=["GET"])
def startup_detail(name):
    name_lower = name.lower()
    print(f"🔍 Looking for startup: {name_lower}")

    for investor in INVESTORS:
        for startup in investor.get("Invested Startups", []):
            if startup.get("Startup Name", "").lower() == name_lower:
                print(f"✅ Found startup '{name}' under investor {investor.get('Name')}")
                return jsonify({
                    "Startup Name": startup.get("Startup Name"),
                    "Industry": startup.get("Industry"),
                    "Location": startup.get("Location"),
                    "Funding Stage": startup.get("Funding Stage"),
                    "Description": startup.get("Description"),
                    "Founded Year": startup.get("Founded Year"),
                    "Team Size": startup.get("Team Size"),
                    "Revenue Stage": startup.get("Revenue Stage"),
                    "Business Model": startup.get("Business Model"),
                    "Customer Segment": startup.get("Customer Segment"),
                    "Investor": investor.get("Name"),
                    "Investor Location": investor.get("Location"),
                }), 200

    print(f"❌ Startup '{name}' not found in any investor's portfolio.")
    return jsonify({"error": "Startup not found"}), 404

@api.route("/dropdowns", methods=["GET"])
def dropdown_options():
    options_path = os.path.join(DATA_DIR, "labels.json")
    if os.path.exists(options_path):
        with open(options_path, "r", encoding="utf-8") as f:
            options = json.load(f)
        return jsonify(options), 200
    else:
        return jsonify({"error": "Dropdown options file not found"}), 404


app.register_blueprint(api)

if __name__ == "__main__":
    app.run(debug=True)
