# GameIQ: AI-Powered Player Behavior Analytics Platform

> 🚀 End-to-end ML + Full Stack Project for Player Churn Prediction

A full-stack data analytics platform that analyzes player behavior in mobile games, predicts player churn using machine learning, and serves predictions through a REST API with a live dashboard.

Built using the **Cookie Cats** A/B testing dataset (90,189 players).

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Node.js](https://img.shields.io/badge/Node.js-Express-green)
![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-orange)
![Flask](https://img.shields.io/badge/API-Flask-lightgrey)

---

## What It Does

- **Analyzes** player retention and engagement patterns from A/B test data
- **Predicts** whether a player will churn (leave the game) within 7 days
- **Serves** predictions through a Flask API + Node.js backend
- **Displays** results in a clean analytics dashboard with interactive charts

---

## 💡 Why This Project Matters

This project simulates how real gaming companies analyze player behavior and optimize retention.

It demonstrates:
- End-to-end ML pipeline development
- Real-world A/B testing analysis
- Production-style API architecture (Node + Flask)
- Data-driven decision making

This is not just a model — it's a **complete product system**.

---

## Architecture

```
Frontend (HTML/CSS/JS)  -->  Node.js Backend (Express :3000)  -->  Flask ML API (:5000)  -->  model.pkl
         UI                        Middleware / Proxy                 Prediction Engine        RandomForest
```

---

## Project Structure

```
GameIQ/
├── data/
│   └── cookie_cats.csv          # Dataset (90K players)
├── ml-model/
│   ├── analysis.py              # EDA + visualizations
│   ├── model.py                 # ML training pipeline
│   ├── app.py                   # Flask API server
│   ├── model.pkl                # Trained model
│   └── venv/                    # Python virtual environment
├── backend/
│   ├── server.js                # Node.js Express server
│   └── package.json
├── frontend/
│   ├── index.html               # Dashboard UI
│   ├── style.css                # Styles
│   ├── script.js                # Charts + prediction logic
│   └── charts/                  # Generated EDA charts
├── BUSINESS_INSIGHTS.md         # Analysis report
└── README.md
```

---

## Key Results

| Metric | Value |
|--------|-------|
| Dataset Size | 90,189 players |
| Churn Rate | 81.4% |
| Model Accuracy | 86.79% |
| F1 Score (Churn) | 0.92 |
| Top Feature | Game rounds played (86.2% importance) |
| A/B Test Winner | gate_30 (19.0% vs 18.2% Day 7 retention) |

---

## 📸 Screenshots

_Add your dashboard screenshots here (recommended for recruiters)_

---

## Setup & Run

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Clone the repo
```bash
git clone https://github.com/Mansehaj12/GameIQ-Player-Churn-Prediction.git
cd GameIQ
```

### 2. Set up the ML environment
```bash
cd ml-model
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install pandas numpy scikit-learn flask matplotlib seaborn
```

### 3. Run EDA and train the model
```bash
python analysis.py   # Generates charts + analysis
python model.py      # Trains model, saves model.pkl
```

### 4. Start the Flask API
```bash
python app.py        # Runs on http://localhost:5000
```

### 5. Set up and start the Node.js backend
```bash
cd ../backend
npm install
node server.js       # Runs on http://localhost:3000
```

### 6. Open the dashboard
Open `http://localhost:3000` in your browser.

---

## API Endpoints

### Flask ML API (port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/predict` | Predict churn |

### Node.js Backend (port 3000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/predict` | Predict churn (proxies to Flask) |
| POST | `/api/predict/batch` | Batch predictions |
| GET | `/api/stats` | ML API status |

### Example Request
```bash
curl -X POST http://localhost:3000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"rounds": 50, "retention_1": 1, "version": "gate_30"}'
```

### Example Response
```json
{
  "success": true,
  "data": {
    "prediction": 1,
    "label": "CHURNED",
    "probability": 76.5,
    "details": {
      "retain_probability": 23.5,
      "churn_probability": 76.5
    }
  }
}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Analysis | Python, Pandas, Matplotlib, Seaborn |
| Machine Learning | scikit-learn (RandomForestClassifier) |
| ML API | Flask |
| Backend | Node.js, Express, Axios |
| Frontend | HTML, CSS, JavaScript, Chart.js |

---

## Business Insights

1. **81% churn is normal** for free-to-play — but even 1% improvement = 900+ more active players
2. **Gate at level 30 wins** the A/B test — do not move it to 40
3. **Engagement is everything** — players past 50 rounds retain dramatically better
4. **Day 1 return is critical** — if they don't come back in 24h, they're gone
5. **Recommendation:** Optimize first 10 rounds, add push notifications at 12h, implement daily login rewards

See full report: [BUSINESS_INSIGHTS.md](./BUSINESS_INSIGHTS.md)

---

## Future Enhancements
- 🚀 **Deploy to Cloud**: Host frontend on Vercel/Netlify, backend on Render/Heroku.
- 🌙 **Dark Mode Support**: Allow users to toggle between light and dark themes.
- 🤖 **Advanced ML Models**: Implement XGBoost or LightGBM for improved accuracy and handle class imbalance using SMOTE.
- 📊 **Extended Dashboard**: Add more real-time visual charts and interactive data filtering.
- 🔑 **Authentication**: Secure the backend APIs with JWT tokens.

---

## License

MIT

---

## Author

👨‍💻 **Mansehaj Preet Singh**

Built as a full-stack data science project demonstrating:
- Machine Learning (churn prediction)
- Backend API development
- Product analytics & A/B testing
- End-to-end system design
