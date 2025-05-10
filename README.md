
# 🧠 Investor Recommender System (Startup Matchmaker)

This is a full-stack **startup-investor recommendation system** using React + Flask + a hybrid recommender engine. It helps match startups with potential investors based on domain, funding stage, and investment patterns.


---

## 🚀 Features

- ✅ frontend with industry/stage selectors
- ✅ Flask-based backend API
- ✅ Content-based filtering using encoded features
- ✅ Collaborative filtering using interaction history
- ✅ Hybrid recommendations with customizable weights
- ✅ CORS-enabled API for local frontend-backend interaction
- ✅ JSON-safe response handling

---

## 📁 Project Structure

```
.
├── app/
│   ├── api.py                      # Flask API routes
│   ├── recommender_engine.py       # Recommendation logic (content/collab/hybrid)
│   ├── utils.py                    # Data loading and input encoding
│   └── data/
│       ├── investors_encoded.csv   # One-hot encoded investor data
│       ├── interaction_matrix.csv  # Investor-startup interactions
│       └── investors.json          # (Optional) Raw investor details
├── frontend/
│   └── src/App.jsx                 # Main React app
```

---

## 🧪 How to Run

### 🔧 Backend

1. Install Python packages:
   ```bash
   pip install flask flask-cors scikit-learn pandas numpy
   ```

2. Start the Flask server:
   ```bash
   python app/api.py
   ```

The API will be live at: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

### 🎨 Frontend

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the app:
   ```bash
   npm run dev
   ```

Frontend is served at: [http://localhost:5173/](http://localhost:5173/)

---

## 🧠 Recommendation Types

| Type           | Logic                                                                 |
|----------------|-----------------------------------------------------------------------|
| `content`      | One-hot encoded matching of industries + stages + normalized metrics |
| `collaborative`| Popularity-based fallback using interaction matrix                   |
| `hybrid`       | Weighted combo: `0.6*content + 0.4*collaborative`                    |

---

## 🛡️ Notes

- Ensure that column names in `investors_encoded.csv` match industry/stage options in the frontend.
- Use consistent formatting (e.g., "FinTech" vs "Fintech").
- Backend responses are sanitized to avoid JSON serialization errors.

---

## 👨‍💻 Author

Built with ❤️ by startup recommender enthusiasts.

