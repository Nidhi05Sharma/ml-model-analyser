import { useState } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");

  const [file, setFile] = useState(null);
  const [learningType, setLearningType] = useState("supervised");
  const [problemType, setProblemType] = useState("classification");
  const [model, setModel] = useState("logistic_regression");

  const [result, setResult] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [showVisualization, setShowVisualization] = useState(false);
  const [chartType, setChartType] = useState("bar");

  const handleLogin = async (e) => {
    e.preventDefault();

    setLoginError("");

    const response = await fetch(
      `https://ml-model-analyser-1.onrender.com/api/login?username=${encodeURIComponent(
        username
      )}&password=${encodeURIComponent(password)}`,
      {
        method: "POST",
      }
    );

    const data = await response.text();

    if (response.ok && data === "Login successful") {
      setIsLoggedIn(true);
    } else {
      setLoginError("Invalid username or password.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Please select a dataset.");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);
    formData.append("learning_type", learningType);
    formData.append("problem_type", problemType);
    formData.append("model", model);

    const response = await fetch(
      "https://ml-model-analyser-1.onrender.com/api/train",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error("Training failed:", data);
      setResult(null);
      alert("Training failed. Check the Spring Boot terminal.");
      return;
    }

    setResult(data);
    setShowVisualization(false);
    setExperiments([]);
  };

  const handleVisualize = async () => {
    if (!result) {
      return;
    }

    const response = await fetch(
      `https://ml-model-analyser-1.onrender.com/api/experiments?filename=${encodeURIComponent(
        result.filename
      )}`
    );

    const data = await response.json();

    if (!response.ok) {
      console.error("Failed to fetch experiments:", data);
      alert("Could not load experiment data.");
      return;
    }

    setExperiments(data);
    setShowVisualization(true);
  };

  const chartData = experiments
    .filter((experiment) => experiment.accuracy !== null)
    .map((experiment) => ({
      model: experiment.model,
      accuracy: Number(experiment.accuracy),
    }));

  if (!isLoggedIn) {
    return (
      <div className="app">
        <div className="train-card">
          <h1>ML Model Analyzer</h1>

          <p className="subtitle">Login to access the analyzer</p>

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Username</label>

              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
              />
            </div>

            <button type="submit">Login</button>
          </form>

          {loginError && (
            <p style={{ color: "red", marginTop: "15px" }}>
              {loginError}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <h1>ML Model Analyzer</h1>

      <p className="subtitle">
        Train and analyze machine learning models
      </p>

      <div className="train-card">
        <h2>Train Model</h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Dataset</label>

            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </div>

          <div className="form-group">
            <label>Learning Type</label>

            <select
              value={learningType}
              onChange={(e) => setLearningType(e.target.value)}
            >
              <option value="supervised">Supervised</option>
              <option value="unsupervised">Unsupervised</option>
            </select>
          </div>

          <div className="form-group">
            <label>Problem Type</label>

            <select
              value={problemType}
              onChange={(e) => setProblemType(e.target.value)}
            >
              <option value="classification">Classification</option>
              <option value="regression">Regression</option>
              <option value="clustering">Clustering</option>
            </select>
          </div>

          <div className="form-group">
            <label>Model</label>

            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              <option value="logistic_regression">
                Logistic Regression
              </option>

              <option value="decision_tree">
                Decision Tree
              </option>

              <option value="random_forest">
                Random Forest
              </option>

              <option value="svm">
                SVM
              </option>
            </select>
          </div>

          <button type="submit">Train Model</button>
        </form>
      </div>

      {result && (
        <div className="results-section">
          <h2>Training Result</h2>

          <div className="info-grid">
            <div className="info-card">
              <span>Dataset</span>
              <strong>{result.filename}</strong>
            </div>

            <div className="info-card">
              <span>Learning Type</span>
              <strong>{result.learning_type}</strong>
            </div>

            <div className="info-card">
              <span>Problem Type</span>
              <strong>{result.problem_type}</strong>
            </div>

            <div className="info-card">
              <span>Model</span>
              <strong>{result.model}</strong>
            </div>

            <div className="info-card">
              <span>Rows</span>
              <strong>{result.rows}</strong>
            </div>

            <div className="info-card">
              <span>Features</span>
              <strong>{result.features}</strong>
            </div>

            <div className="info-card">
              <span>Target</span>
              <strong>{result.target || "N/A"}</strong>
            </div>
          </div>

          <h3>Metrics</h3>

          <div className="metrics-grid">
            {Object.entries(result.results || {}).map(([key, value]) => (
              <div className="metric-card" key={key}>
                <span>{key.replaceAll("_", " ")}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>

          <h3>Model Comparison</h3>

          <button type="button" onClick={handleVisualize}>
            Visualize
          </button>

          {showVisualization && (
            <div className="visualization-section">
              <div className="form-group">
                <label>Graph Type</label>

                <select
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value)}
                >
                  <option value="bar">Bar Chart</option>
                  <option value="pie">Pie Chart</option>
                </select>
              </div>

              {experiments.length === 0 ? (
                <p>No experiment data found for this dataset.</p>
              ) : chartData.length === 0 ? (
                <p>
                  No accuracy data is available for these experiments.
                </p>
              ) : (
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={350}>
                    {chartType === "bar" ? (
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="model" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="accuracy" />
                      </BarChart>
                    ) : (
                      <PieChart>
                        <Pie
                          data={chartData}
                          dataKey="accuracy"
                          nameKey="model"
                          cx="50%"
                          cy="50%"
                          outerRadius={120}
                          label
                        >
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} />
                          ))}
                        </Pie>

                        <Tooltip />
                      </PieChart>
                    )}
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;

