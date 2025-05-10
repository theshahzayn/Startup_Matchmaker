from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender_engine import (
    recommend_content,
    recommend_collaborative,
    recommend_hybrid,
    recommend_similar_startups
)

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "Investor Recommender System API is live."

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    rs_type = data.get("rs_type", "content").lower()

    try:
        if rs_type == "content":
            result = recommend_content(data)
        elif rs_type == "collaborative":
            result = recommend_collaborative(data)
        elif rs_type == "hybrid":
            result = recommend_hybrid(data)
        elif rs_type == "startup_similarity":
            # Now uses industries & stages directly
            result = recommend_similar_startups(data)
        else:
            return jsonify({"error": "Invalid rs_type. Use: content, collaborative, hybrid, startup_similarity"}), 400

        return jsonify({"recommendations": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
