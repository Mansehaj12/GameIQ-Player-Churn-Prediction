// ============================================================
// GameIQ - Step 6: Node.js Backend (Express Server)
// ============================================================
//
// PURPOSE:
//   This server acts as a MIDDLEWARE between the frontend and
//   the Flask ML API. Why not call Flask directly from the frontend?
//
//   1. SECURITY: The Flask API URL stays hidden from the browser.
//   2. VALIDATION: We validate input before forwarding to ML API.
//   3. LOGGING: We can track all prediction requests.
//   4. FLEXIBILITY: We can add auth, caching, rate-limiting later.
//   5. AGGREGATION: We can combine data from multiple services.
//
// ARCHITECTURE:
//   [Frontend] --> [Node.js :3000] --> [Flask ML API :5000]
//       UI           Middleware          Model Prediction
//
// ============================================================

const express = require("express");
const axios = require("axios");
const cors = require("cors");
const path = require("path");

const app = express();
const PORT = 3000;
const FLASK_API_URL = "http://127.0.0.1:5000";

// ────────────────────────────────────────────────────────────
// MIDDLEWARE
// ────────────────────────────────────────────────────────────

// CORS: Allow frontend (any origin in dev) to call this API
app.use(cors());

// Parse JSON request bodies
app.use(express.json());

// Serve static files from the frontend folder
// This lets us serve the frontend directly from this server
app.use(express.static(path.join(__dirname, "..", "frontend")));

// Request logger - logs every incoming request
app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${req.method} ${req.url}`);
    next();
});

// ────────────────────────────────────────────────────────────
// ROUTE: Health Check
// ────────────────────────────────────────────────────────────
// GET /
// Quick way to verify the backend is running

app.get("/api/health", (req, res) => {
    res.json({
        status: "online",
        service: "GameIQ Backend",
        timestamp: new Date().toISOString(),
        ml_api: FLASK_API_URL,
        endpoints: {
            "GET  /api/health": "Health check (this endpoint)",
            "POST /api/predict": "Predict player churn",
            "GET  /api/stats": "Get dataset statistics from ML API",
        },
    });
});

// ────────────────────────────────────────────────────────────
// ROUTE: Predict Churn
// ────────────────────────────────────────────────────────────
// POST /api/predict
//
// HOW THIS WORKS:
//   1. Frontend sends: { rounds: 50, retention_1: 1, version: "gate_30" }
//   2. We VALIDATE the input (check types, ranges, required fields)
//   3. We FORWARD the request to Flask API (http://localhost:5000/predict)
//   4. Flask loads model.pkl, runs prediction, returns result
//   5. We send the result back to the frontend
//
// This is a PROXY pattern - Node.js sits between frontend and ML API.

app.post("/api/predict", async (req, res) => {
    try {
        const { rounds, retention_1, version } = req.body;

        // ── Input Validation ──
        // Always validate before sending to ML API to prevent bad data

        if (rounds === undefined || retention_1 === undefined || !version) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields",
                required: {
                    rounds: "number (total game rounds played)",
                    retention_1: "number (1 = returned day 1, 0 = did not)",
                    version: "string ('gate_30' or 'gate_40')",
                },
                example: {
                    rounds: 50,
                    retention_1: 1,
                    version: "gate_30",
                },
            });
        }

        // Validate data types and ranges
        const parsedRounds = Number(rounds);
        const parsedRetention = Number(retention_1);

        if (isNaN(parsedRounds) || parsedRounds < 0) {
            return res.status(400).json({
                success: false,
                error: "'rounds' must be a non-negative number",
            });
        }

        if (![0, 1].includes(parsedRetention)) {
            return res.status(400).json({
                success: false,
                error: "'retention_1' must be 0 or 1",
            });
        }

        if (!["gate_30", "gate_40"].includes(version)) {
            return res.status(400).json({
                success: false,
                error: "'version' must be 'gate_30' or 'gate_40'",
            });
        }

        // ── Forward to Flask ML API ──
        const startTime = Date.now();

        const flaskResponse = await axios.post(`${FLASK_API_URL}/predict`, {
            rounds: parsedRounds,
            retention_1: parsedRetention,
            version: version,
        });

        const responseTime = Date.now() - startTime;

        // ── Send response back to frontend ──
        console.log(
            `    -> Prediction: ${flaskResponse.data.label} (${responseTime}ms)`
        );

        res.json({
            success: true,
            data: flaskResponse.data,
            meta: {
                response_time_ms: responseTime,
                source: "GameIQ ML API",
            },
        });
    } catch (error) {
        // ── Error Handling ──
        console.error(`    -> ERROR: ${error.message}`);

        // Check if Flask API is down
        if (error.code === "ECONNREFUSED") {
            return res.status(503).json({
                success: false,
                error: "ML API is not running",
                hint: "Start the Flask server: cd ml-model && python app.py",
            });
        }

        // Flask returned an error
        if (error.response) {
            return res.status(error.response.status).json({
                success: false,
                error: error.response.data.error || "ML API error",
            });
        }

        // Unknown error
        res.status(500).json({
            success: false,
            error: "Internal server error",
            message: error.message,
        });
    }
});

// ────────────────────────────────────────────────────────────
// ROUTE: Get ML API Stats
// ────────────────────────────────────────────────────────────
// GET /api/stats
// Proxy to Flask health check to verify ML API connectivity

app.get("/api/stats", async (req, res) => {
    try {
        const response = await axios.get(`${FLASK_API_URL}/`);
        res.json({
            success: true,
            ml_api_status: "connected",
            data: response.data,
        });
    } catch (error) {
        res.status(503).json({
            success: false,
            ml_api_status: "disconnected",
            error: "Cannot reach ML API",
            hint: "Make sure Flask is running on port 5000",
        });
    }
});

// ────────────────────────────────────────────────────────────
// ROUTE: Batch Predict (bonus - predict for multiple players)
// ────────────────────────────────────────────────────────────
// POST /api/predict/batch
// Input: { players: [ {rounds, retention_1, version}, ... ] }
// Output: Array of predictions

app.post("/api/predict/batch", async (req, res) => {
    try {
        const { players } = req.body;

        if (!Array.isArray(players) || players.length === 0) {
            return res.status(400).json({
                success: false,
                error: "Provide an array of players",
                example: {
                    players: [
                        { rounds: 10, retention_1: 0, version: "gate_30" },
                        { rounds: 200, retention_1: 1, version: "gate_40" },
                    ],
                },
            });
        }

        if (players.length > 100) {
            return res.status(400).json({
                success: false,
                error: "Maximum 100 players per batch",
            });
        }

        // Send all predictions in parallel
        const predictions = await Promise.all(
            players.map((player) =>
                axios
                    .post(`${FLASK_API_URL}/predict`, {
                        rounds: player.rounds,
                        retention_1: player.retention_1,
                        version: player.version,
                    })
                    .then((r) => ({ success: true, ...r.data }))
                    .catch((e) => ({
                        success: false,
                        error: e.message,
                        input: player,
                    }))
            )
        );

        res.json({
            success: true,
            count: predictions.length,
            predictions,
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
        });
    }
});

// ────────────────────────────────────────────────────────────
// 404 HANDLER - Catch unknown routes
// ────────────────────────────────────────────────────────────

app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: `Route not found: ${req.method} ${req.url}`,
        available_routes: [
            "GET  /api/health",
            "POST /api/predict",
            "POST /api/predict/batch",
            "GET  /api/stats",
        ],
    });
});

// ────────────────────────────────────────────────────────────
// START SERVER
// ────────────────────────────────────────────────────────────

app.listen(PORT, () => {
    console.log("==================================================");
    console.log("  GameIQ Backend Server");
    console.log(`  Running on: http://localhost:${PORT}`);
    console.log(`  ML API:     ${FLASK_API_URL}`);
    console.log("==================================================");
    console.log("  Endpoints:");
    console.log("  GET  /api/health        - Health check");
    console.log("  POST /api/predict       - Predict churn");
    console.log("  POST /api/predict/batch  - Batch predict");
    console.log("  GET  /api/stats         - ML API status");
    console.log("==================================================");
});
