import { useState } from "react";
import axios from "axios";
import "./index.css";

const industriesList = [
  "AgriTech", "Consumer", "Consumer Internet", "E-commerce", "EdTech",
  "Education", "FinTech", "Financial Inclusion", "Fintech", "Healthcare",
  "Healthtech", "ICT", "Impact", "Logistics", "MarTech", "Media",
  "Mobility", "On-demand", "Platforms", "PropTech", "Retailtech",
  "Sector Agnostic", "Social Tech", "Software", "Tech", "Technology",
  "Technology (Sector Agnostic)", "Various"
];

const stagesList = [
  "Accelerator", "Growth", "Pre-Seed", "Seed", "Series A", "Series B", "Series C"
];

const rsTypes = ["content", "collaborative", "hybrid", "startup_similarity"];

export default function App() {
  const [industries, setIndustries] = useState([]);
  const [stages, setStages] = useState([]);
  const [rsType, setRsType] = useState("hybrid");
  const [activityWeight, setActivityWeight] = useState(0.5);
  const [investmentWeight, setInvestmentWeight] = useState(0.5);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const toggle = (list, item, setter) =>
    setter(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      let payload = { industries, stages };

      // for non-startup_similarity, include RS type & weights
      if (rsType !== "startup_similarity") {
        payload = {
          ...payload,
          rs_type: rsType,
          activityWeight,
          investmentWeight
        };
      }

      const url =
        rsType === "startup_similarity"
          ? "/recommend/startup"
          : "/recommend";

      const res = await axios.post("http://127.0.0.1:5000/recommend", payload);

      if (res.data.recommendations) {
        setResults(res.data.recommendations);
      } else {
        alert("Unexpected API response");
        setResults([]);
      }
    } catch (error) {
      console.error("API Request Failed:", error);
      alert("Network or server error. Check the Flask backend.");
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#141414] text-white font-sans px-6 py-12">
      <h1 className="text-4xl font-extrabold text-center text-red-500 mb-10">
        🎯 Startup ↔ Investor Match
      </h1>

      <div className="max-w-3xl mx-auto bg-[#1f1f1f] rounded-xl p-6 shadow-xl space-y-6">
        {/* Industries */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">Industries</label>
          <div className="flex flex-wrap gap-2">
            {industriesList.map(ind => (
              <button
                key={ind}
                onClick={() => toggle(industries, ind, setIndustries)}
                className={`px-4 py-2 rounded-full transition-all ${
                  industries.includes(ind)
                    ? "bg-red-500 text-white"
                    : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                }`}
              >
                {ind}
              </button>
            ))}
          </div>
        </section>

        {/* Funding Stages */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">Funding Stages</label>
          <div className="flex flex-wrap gap-2">
            {stagesList.map(stage => (
              <button
                key={stage}
                onClick={() => toggle(stages, stage, setStages)}
                className={`px-4 py-2 rounded-full transition-all ${
                  stages.includes(stage)
                    ? "bg-green-500 text-white"
                    : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                }`}
              >
                {stage}
              </button>
            ))}
          </div>
        </section>

        {/* Weights (only if not startup_similarity) */}
        {rsType !== "startup_similarity" && (
          <>
            <section>
              <label className="text-sm uppercase text-gray-400 block mb-1">
                Recent Activity Preference
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={activityWeight}
                onChange={e => setActivityWeight(parseFloat(e.target.value))}
                className="w-full"
              />
              <p className="text-gray-400 text-sm">Preference: {activityWeight}</p>
            </section>

            <section>
              <label className="text-sm uppercase text-gray-400 block mb-1">
                Investment Experience Preference
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={investmentWeight}
                onChange={e => setInvestmentWeight(parseFloat(e.target.value))}
                className="w-full"
              />
              <p className="text-gray-400 text-sm">Preference: {investmentWeight}</p>
            </section>
          </>
        )}

        {/* Strategy Selector */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">Recommendation Strategy</label>
          <select
            className="w-full bg-gray-800 border border-gray-600 rounded-lg p-2 text-white"
            value={rsType}
            onChange={e => setRsType(e.target.value)}
          >
            {rsTypes.map(type => (
              <option key={type} value={type}>
                {type.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase())}
              </option>
            ))}
          </select>
        </section>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          className="w-full bg-red-600 hover:bg-red-700 py-3 rounded-lg text-lg font-semibold transition-all"
        >
          {loading ? "Finding Matches..." : "Match Investors"}
        </button>
      </div>

      {/* Results Grid */}
      <div className="mt-12 max-w-5xl mx-auto grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {results.map((inv, idx) => (
          <div
            key={idx}
            className="bg-[#1f1f1f] rounded-xl p-5 shadow-lg hover:shadow-red-500/20 transition-shadow border border-gray-800"
          >
            <h2 className="text-xl font-bold text-red-400">{inv["Investor Name"]}</h2>
            <p className="text-gray-400 text-sm mb-2">
              {inv.Location || "Location N/A"}
            </p>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>
                <span className="text-gray-400">Score:</span> {inv.Score}
              </li>
              <li>
                <span className="text-gray-400">Ticket Size:</span> {inv["Ticket Size"] || "—"}
              </li>
              <li>
                <span className="text-gray-400">Recent Year:</span>{" "}
                {inv["Recent Activity Year"] || "—"}
              </li>
              <li>
                <span className="text-gray-400">Investments:</span>{" "}
                {inv["Number of Investments"] || "—"}
              </li>
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
