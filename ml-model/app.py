# ============================================================
# GameIQ - Step 5: Flask ML API (FINAL VERSION)
# ============================================================

from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os
import time

# ── Initialize Flask App ──
app = Flask(__name__)

# ── Load Model Once ──
model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')

with open(model_path, 'rb') as f:
    model = pickle.load(f)

print(f"[*] Model loaded from: {model_path}")


# ============================================================
# HEALTH CHECK ENDPOINT
# ============================================================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "GameIQ ML API is running 🚀",
        "endpoints": {
            "/predict": "POST - Predict player churn",
            "/": "GET - Health check"
        }
    })


# ============================================================
# PREDICT ENDPOINT
# ============================================================

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()

    try:
        data = request.get_json()

        # ── Check JSON exists ──
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # ── Extract values (support both names) ──
        rounds = data.get('sum_gamerounds') or data.get('rounds')
        retention_1 = data.get('retention_1')
        version = data.get('version')

        # ── Validate fields ──
        if rounds is None:
            return jsonify({"error": "Missing 'rounds' or 'sum_gamerounds'"}), 400
        if retention_1 is None:
            return jsonify({"error": "Missing 'retention_1'"}), 400
        if version is None:
            return jsonify({"error": "Missing 'version'"}), 400

        # ── Convert types ──
        rounds = int(rounds)
        retention_1 = int(retention_1)

        # ── Validate values ──
        if rounds < 0:
            return jsonify({"error": "rounds must be >= 0"}), 400
        if retention_1 not in [0, 1]:
            return jsonify({"error": "retention_1 must be 0 or 1"}), 400

        # ── Convert version ──
        if version == 'gate_40':
            version_num = 1
        elif version == 'gate_30':
            version_num = 0
        else:
            return jsonify({
                "error": "Invalid version. Use 'gate_30' or 'gate_40'"
            }), 400

        # ── Prepare input ──
        input_data = pd.DataFrame({
            'sum_gamerounds': [rounds],
            'retention_1_num': [retention_1],
            'version_num': [version_num]
        })

        # ── Prediction ──
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0]

        # ── Response time ──
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)

        # ── Build response ──
        result = {
            "prediction": int(prediction),
            "label": "CHURNED" if prediction == 1 else "RETAINED",
            "confidence": round(max(probability) * 100, 2),
            "probabilities": {
                "retain": round(probability[0] * 100, 2),
                "churn": round(probability[1] * 100, 2)
            },
            "input": {
                "rounds": rounds,
                "retention_1": retention_1,
                "version": version
            },
            "meta": {
                "model": "RandomForestClassifier",
                "response_time_ms": response_time
            }
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("[*] GameIQ ML API")
    print("Running on: http://localhost:5000")
    print("Endpoints:")
    print("  GET  /        -> Health check")
    print("  POST /predict -> Churn prediction")
    print("=" * 50 + "\n")

    app.run(debug=True, port=5000)