# GameIQ - Resume & Interview Content

---

## Resume Bullet Points

Use 2-3 of these on your resume under "Projects":

**GameIQ: AI-Powered Player Behavior Analytics Platform**

- Built an end-to-end churn prediction system analyzing 90K+ mobile game players, achieving 86.8% accuracy using RandomForest, with a Flask API serving real-time predictions to a Node.js backend and interactive dashboard.

- Performed A/B test analysis on player retention data, identifying that gate placement at level 30 increases Day 7 retention by 0.82% over level 40, translating to measurable player lifetime value improvement.

- Developed a full-stack analytics platform with Python (pandas, scikit-learn, Flask), Node.js (Express), and vanilla JavaScript (Chart.js), demonstrating ETL pipeline, model training, API design, and data visualization skills.

- Engineered a churn prediction ML pipeline with feature importance analysis, finding that game engagement (86.2% importance) and Day 1 retention (13.7%) are the strongest predictors of player churn.

---

## Short Project Explanation (for interviews)

**"Tell me about a project you've worked on."**

> "I built GameIQ, a player analytics platform that predicts churn in mobile games. I used the Cookie Cats dataset — about 90,000 players from an A/B test where they moved a difficulty gate from level 30 to level 40.
>
> I started with exploratory data analysis to understand retention patterns. The key finding was that 81% of players churn within 7 days, and engagement in the first few sessions is the strongest predictor of long-term retention.
>
> I trained a Random Forest model that predicts churn with about 87% accuracy. The model showed that game rounds played accounts for 86% of the prediction importance — much more than the A/B test group.
>
> I then built a Flask API to serve predictions and a Node.js backend as middleware, and connected it to a dashboard where you can input a player profile and get a real-time prediction. The dashboard also shows charts for retention rates, A/B test results, and engagement patterns.
>
> The business takeaway was to keep the gate at level 30 — it actually had better retention — and to focus on getting players past their first 50 rounds, which is where we saw the biggest drop in churn rate."

---

## Technical Interview Q&A

**Q: Why did you choose Random Forest over other models?**

> It handles mixed feature types well, provides feature importance out of the box, doesn't require feature scaling, and is resistant to overfitting through ensemble averaging. For a tabular dataset with 3 features, it gives strong performance without complex tuning.

**Q: How would you improve the model accuracy?**

> I'd engineer more features — like rounds per session, time between sessions, and progression speed. I'd also try gradient boosting (XGBoost/LightGBM) and address the class imbalance (81/19 split) using SMOTE or class weights.

**Q: How does the architecture work?**

> The frontend sends requests to a Node.js Express server on port 3000. Node.js validates the input and proxies the request to a Flask API on port 5000, which loads the pickled model and returns the prediction. This separation allows independent scaling and keeps the ML model URL hidden from the client.

**Q: What's the business value of this project?**

> In a real gaming company, even a 1% improvement in Day 7 retention across 90K players means ~900 more active players. If each player generates $0.10/day in ad revenue, that's $900/day or $328K/year in additional revenue. The model helps identify at-risk players for targeted interventions before they churn.

---

## LinkedIn Post (optional)

> Just shipped GameIQ — a full-stack player analytics platform that predicts churn in mobile games using machine learning.
>
> Analyzed 90K players from a real A/B test, built a Random Forest model (87% accuracy), served predictions through Flask + Node.js, and visualized insights in a live dashboard.
>
> Key finding: Engagement in the first 50 game rounds is the single strongest predictor of long-term retention.
>
> Tech: Python | scikit-learn | Flask | Node.js | Express | Chart.js
>
> #datascience #machinelearning #analytics #fullstack
