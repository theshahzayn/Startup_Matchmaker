import axios from "axios";
import "./index.css";
import { useState, useEffect } from "react";

const rsTypes = ["content", "collaborative", "hybrid", "startup_similarity"];
const YEAR_BUCKETS = ["New", "Growing", "Established", "Unknown"]

export default function App() {
  const [industries, setIndustries] = useState([]);
  const [stages, setStages] = useState([]);
  const [rsType, setRsType] = useState("hybrid");
  const [activityWeight, setActivityWeight] = useState(0.5);
  const [investmentWeight, setInvestmentWeight] = useState(0.5);
  const [results, setResults] = useState([]);
  const [teamSize, setTeamSize] = useState("");
  const [foundedYear, setFoundedYear] = useState("");
  const [location, setLocation] = useState("");
  const [businessModel, setBusinessModel] = useState("");
  const [dropdowns, setDropdowns] = useState({ industries: [], stages: [], locations: [] });
  const [loading, setLoading] = useState(false);
  const [revenueStage, setRevenueStage] = useState("");
  const [customerSegment, setCustomerSegment] = useState("");


  useEffect(() => {
    axios.get("http://127.0.0.1:5000/dropdowns")
      .then(res => setDropdowns(res.data))
      .catch(err => console.error("Failed to load dropdowns:", err));
  }, []);

  const toggle = (list, item, setter) =>
    setter(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const payload = {
        industries,
        stages,
        rs_type: rsType,
        ...(rsType === "hybrid" && {
          activityWeight,
          investmentWeight
        }),
        teamSize,
        foundedYear,
        location,
        businessModel,
        revenueStage,
        customerSegment
      };

      const res = await axios.post("http://127.0.0.1:5000/recommend", payload);

      if (res.data.recommendations) {
        setResults(res.data.recommendations);
      } else {
        alert("Unexpected API response");
        setResults([]);
      }
    } catch (error) {
      console.error("API error:", error);
      alert("Server error. Is Flask running?");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#141414] text-white font-sans px-6 py-12">
      <h1 className="text-4xl font-extrabold text-center text-red-500 mb-10">
        Startup ↔ Investor Match
      </h1>

      <div className="max-w-3xl mx-auto bg-[#1f1f1f] rounded-xl p-6 shadow-xl space-y-6">
        {/* Strategy Type */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">
            Recommendation Strategy
          </label>
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

        {/* Industries */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">
            Industries
          </label>
          <div className="flex flex-wrap gap-2">
            {dropdowns.industries.map(ind => (
              <button
                key={ind}
                onClick={() => toggle(industries, ind, setIndustries)}
                className={`px-4 py-2 rounded-full ${
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

        {/* Stages */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">
            Funding Stages
          </label>
          <div className="flex flex-wrap gap-2">
            {dropdowns.stages.map(stage => (
              <button
                key={stage}
                onClick={() => toggle(stages, stage, setStages)}
                className={`px-4 py-2 rounded-full ${
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

        {/* Hybrid Sliders */}
        {rsType === "hybrid" && (
          <>
            <section>
              <label className="text-sm text-gray-400 block mb-1">
                Activity Weight
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
              <p className="text-sm text-gray-400">Current: {activityWeight}</p>
            </section>

            <section>
              <label className="text-sm text-gray-400 block mb-1">
                Investment Weight
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
              <p className="text-sm text-gray-400">Current: {investmentWeight}</p>
            </section>
          </>
        )}

        {/* Team Size */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">
            Team Size
          </label>
          <select
            value={teamSize}
            onChange={e => setTeamSize(e.target.value)}
            className="w-full bg-gray-800 text-white p-2 rounded-lg border border-gray-600"
          >
            <option value="">Select team size</option>
            {dropdowns.team_sizes?.map(size => (
              <option key={size} value={size}>{size}</option>
            ))}
          </select>
        </section>

        {/* Revenue Stage */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">
            Revenue Stage
          </label>
          <select
            value={revenueStage}
            onChange={e => setRevenueStage(e.target.value)}
            className="w-full bg-gray-800 text-white p-2 rounded-lg border border-gray-600"
          >
            <option value="">Select revenue stage</option>
            {dropdowns.revenue_stages?.map(stage => (
              <option key={stage} value={stage}>{stage}</option>
            ))}
          </select>
        </section>

        {/* Customer Segment */}
        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">
            Customer Segment
          </label>
          <select
            value={customerSegment}
            onChange={e => setCustomerSegment(e.target.value)}
            className="w-full bg-gray-800 text-white p-2 rounded-lg border border-gray-600"
          >
            <option value="">Select customer segment</option>
            {dropdowns.customer_segments?.map(seg => (
              <option key={seg} value={seg}>{seg}</option>
            ))}
          </select>
        </section>

        <section>
        <label className="text-sm uppercase text-gray-400 block mb-2">
            Company maturity
        </label>
        <select
          value={foundedYear}
          onChange={e => setFoundedYear(e.target.value)}
          className="w-full bg-gray-800 text-white p-2 rounded-lg border border-gray-600"
        >

          <option value="">Select company maturity</option>
          {YEAR_BUCKETS.map(year => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>
        </section>

        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">
            Location
          </label>
          <select
            value={location}
            onChange={e => setLocation(e.target.value)}
            className="w-full bg-gray-800 text-white p-2 rounded-lg border border-gray-600"
          >
            <option value="">Select a location</option>
            {dropdowns.locations.map(loc => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </section>


        <section>
          <label className="text-sm uppercase text-gray-400 block mb-2">
            Business Model
          </label>
          <input
            type="text"
            value={businessModel}
            onChange={e => setBusinessModel(e.target.value)}
            className="w-full bg-gray-800 text-white p-2 rounded-lg border border-gray-600"
          />
        </section>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          className="w-full bg-red-600 hover:bg-red-700 py-3 rounded-lg text-lg font-semibold"
        >
          {loading ? "Finding Matches..." : "Match Investors"}
        </button>
      </div>

      {/* Results Grid */}
      <div className="mt-12 max-w-5xl mx-auto grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {rsType === "startup_similarity"
          ? results.map((s, i) => (
              <div key={i} className="bg-[#1f1f1f] rounded-xl p-5 shadow-lg border border-gray-800">
                <h2 className="text-xl font-bold text-blue-400">{s["Startup Name"]}</h2>
                <p className="text-gray-400 text-sm mb-1">Industry: {s.Industry}</p>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li><span className="text-gray-400">Funding Stage:</span> {s["Funding Stage"]}</li>
                  <li><span className="text-gray-400">Score:</span> {s.Score}</li>
                  <li><span className="text-gray-400">Investor:</span> {s.Investor}</li>
                </ul>
              </div>
            ))
          :results.map((inv, i) => (
            <div
              key={i}
              className="bg-[#1f1f1f] rounded-xl p-5 shadow-lg border border-gray-800 space-y-3"
            >
              <h2 className="text-xl font-bold text-red-400">{inv["Investor Name"]}</h2>
              <p className="text-gray-400 text-sm mb-2">{inv.Location}</p>

              <p className="text-sm text-gray-300">{inv["Investor Bio"]}</p>

              <div>
                <span className="text-gray-400 text-sm">Investment Stages:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {Array.isArray(inv["Investment Stages"]) ? inv["Investment Stages"].map((stage, idx) => (
                    <span
                      key={idx}
                      className="bg-green-600 text-white px-3 py-1 rounded-full text-xs"
                    >
                      {stage}
                    </span>
                  )) : <span className="text-gray-300">{inv["Investment Stages"]}</span>}
                </div>
              </div>

              <div>
                <span className="text-gray-400 text-sm">Past Investment Types:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {Array.isArray(inv["Past Investment Types"]) ? inv["Past Investment Types"].map((type, idx) => (
                    <span
                      key={idx}
                      className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs"
                    >
                      {type}
                    </span>
                  )) : <span className="text-gray-300">{inv["Past Investment Types"]}</span>}
                </div>
              </div>

              <ul className="text-sm text-gray-300 space-y-1">
                <li>
                  <span className="text-gray-400">Score:</span> {inv.Score}
                </li>
              </ul>
            </div>

            ))}
      </div>
    </div>
  );
}
